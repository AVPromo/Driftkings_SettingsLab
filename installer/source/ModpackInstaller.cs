// Complete modpack transaction. No destinations come from archive extraction.
using System;
using System.Collections;
using System.Collections.Generic;
using System.IO;
using System.IO.Compression;
using System.Security.Cryptography;
using System.Text;
using System.Text.RegularExpressions;

internal static partial class Installer
{
    static Dictionary<string, object> Map(object value)
    {
        var result = value as Dictionary<string, object>;
        Require(result != null, "Expected object"); return result;
    }

    static IList Items(object value)
    {
        var result = value as IList;
        Require(result != null && result.Count <= 512, "Invalid array"); return result;
    }

    static void Keys(Dictionary<string, object> value, params string[] names)
    {
        Require(value.Count == names.Length, "Unexpected fields");
        foreach (string name in names) Require(value.ContainsKey(name), "Missing field");
    }

    static string Text(Dictionary<string, object> value, string name)
    {
        Require(value.ContainsKey(name) && value[name] is string, "Expected text");
        return (string)value[name];
    }

    static long Size(Dictionary<string, object> value)
    {
        Require(value.ContainsKey("size") && value["size"] is int && (int)value["size"] > 0 && (int)value["size"] <= 64 * 1024 * 1024, "Invalid size");
        return (int)value["size"];
    }

    static string Digest(Dictionary<string, object> value)
    {
        string result = Text(value, "sha256");
        Require(Regex.IsMatch(result, @"\A[0-9a-f]{64}\z"), "Invalid hash"); return result;
    }

    static string Relative(string path)
    {
        Require(path.Length > 0 && path.Length <= 240, "Invalid path length");
        foreach (string part in path.Split('/'))
        {
            Require(Regex.IsMatch(part, @"\A[A-Za-z0-9][A-Za-z0-9_.+\-]*\z") && !part.EndsWith("."), "Invalid path");
            Require(!Regex.IsMatch(part.Split('.')[0], @"\A(CON|PRN|AUX|NUL|COM[1-9]|LPT[1-9])\z", RegexOptions.IgnoreCase), "Reserved path");
        }
        return path;
    }

    static Dictionary<string, object> Sig(object value)
    {
        if (value == null) return null;
        var result = Map(value); Keys(result, "size", "sha256"); Size(result); Digest(result); return result;
    }

    static Dictionary<string, object> EntrySig(Dictionary<string, object> value)
    {
        return new Dictionary<string, object> { { "size", (int)Size(value) }, { "sha256", Digest(value) } };
    }

    static bool EqualSig(object first, object second)
    {
        var a = Sig(first); var b = Sig(second);
        return a == null || b == null ? a == b : Size(a) == Size(b) && Digest(a) == Digest(b);
    }

    static bool MatchSig(string path, object value)
    {
        var expected = Sig(value); Safe(path, false);
        return expected == null ? !File.Exists(path) && !Directory.Exists(path) : Matches(path, Size(expected), Digest(expected));
    }

    static Dictionary<string, Dictionary<string, object>> InventoryFiles(Dictionary<string, object> inventory, string version, string game)
    {
        Keys(inventory, "schema", "packageId", "version", "channel", "gameVersion", "distribution", "files", "defaults");
        Require(inventory["schema"] is int && (int)inventory["schema"] == 1 && Text(inventory, "packageId") == "driftkings.modpack" &&
                Text(inventory, "version") == version && Text(inventory, "gameVersion") == game, "Inventory identity mismatch");
        string channel = Text(inventory, "channel");
        Require(channel == "stable" || channel == "beta", "Invalid channel");
        var distribution = Map(inventory["distribution"]); Keys(distribution, "file", "size", "sha256"); Size(distribution); Digest(distribution);
        Require(Relative(Text(distribution, "file")) == "Driftkings-" + version + "-WoT-" + game + ".zip", "Invalid distribution name");
        var result = new Dictionary<string, Dictionary<string, object>>(StringComparer.Ordinal);
        var seen = new HashSet<string>(StringComparer.OrdinalIgnoreCase);
        int code = 0, defaults = 0, instructions = 0;
        long total = 0;
        foreach (object raw in Items(inventory["files"]))
        {
            var item = Map(raw); Keys(item, "path", "kind", "size", "sha256");
            string path = Relative(Text(item, "path")), kind = Text(item, "kind");
            Require(seen.Add(path), "Duplicate inventory path"); Size(item); Digest(item); total += Size(item);
            if (kind == "code") { Require(path == "mods/" + game + "/Driftkings.wotmod", "Invalid code path"); code++; }
            else if (kind == "dependency")
            {
                string prefix = "mods/" + game + "/";
                Require(path.StartsWith(prefix, StringComparison.Ordinal) && path.Substring(prefix.Length).IndexOf('/') < 0 &&
                        path.EndsWith(".wotmod", StringComparison.Ordinal) && path != prefix + "Driftkings.wotmod", "Invalid dependency path");
            }
            else if (kind == "defaults") { Require(path == "Driftkings-defaults.zip", "Invalid defaults"); defaults++; }
            else if (kind == "instructions") { Require(path == "INSTALL.txt", "Invalid instructions"); instructions++; }
            else Require(false, "Unknown inventory kind");
            result.Add(path, item);
        }
        Require(code == 1 && defaults == 1 && instructions == 1, "Incomplete inventory");
        seen.Clear();
        foreach (object raw in Items(inventory["defaults"]))
        {
            var item = Map(raw); Keys(item, "path", "kind", "size", "sha256");
            string path = Relative(Text(item, "path")); Size(item); Digest(item); total += Size(item);
            Require(seen.Add(path) && Text(item, "kind") == "config" && path.StartsWith("mods/configs/Driftkings/", StringComparison.Ordinal) &&
                    !path.StartsWith("mods/configs/Driftkings/cache/", StringComparison.Ordinal) && path.EndsWith(".json", StringComparison.Ordinal), "Invalid default path");
        }
        Require(seen.Count > 0 && total <= 128L * 1024 * 1024, "Inventory exceeds limit");
        return result;
    }

    static HashSet<string> Owned(object value, Dictionary<string, Dictionary<string, object>> files)
    {
        var result = new HashSet<string>(StringComparer.Ordinal);
        foreach (object path in Items(value))
            Require(path is string && files.ContainsKey((string)path) &&
                    (Text(files[(string)path], "kind") == "code" || Text(files[(string)path], "kind") == "dependency") && result.Add((string)path), "Invalid ownership");
        return result;
    }

    static void ValidateModpackTicket(Dictionary<string, object> ticket)
    {
        Keys(ticket, "schema", "gameVersion", "version", "size", "sha256", "installedVersion", "installedSize", "installedSha256", "inventory", "operations", "previousReceipt", "owned");
        Require(ticket["schema"] is int && (int)ticket["schema"] == 2, "Invalid ticket schema");
        string game = Text(ticket, "gameVersion"), version = Text(ticket, "version"), installed = Text(ticket, "installedVersion");
        Require(Regex.IsMatch(game, @"\A(0|[1-9][0-9]*)(\.(0|[1-9][0-9]*)){3}\z") && version.Length <= 200 && installed.Length <= 200, "Invalid versions");
        Size(ticket); Digest(ticket);
        var installedSig = new Dictionary<string, object> { { "size", ticket["installedSize"] }, { "sha256", ticket["installedSha256"] } }; Sig(installedSig);
        var inventory = Map(ticket["inventory"]);
        var files = InventoryFiles(inventory, version, game);
        Require(EqualSig(EntrySig(Map(inventory["distribution"])), EntrySig(ticket)), "Distribution differs from ticket");
        var previous = new Dictionary<string, Dictionary<string, object>>(StringComparer.Ordinal);
        var previousOwned = new HashSet<string>(StringComparer.Ordinal);
        if (ticket["previousReceipt"] != null)
        {
            string raw = Text(ticket, "previousReceipt"); Require(Encoding.UTF8.GetByteCount(raw) <= 65536, "Receipt exceeds limit");
            var receipt = Json.Deserialize<Dictionary<string, object>>(raw); Keys(receipt, "schema", "inventory", "owned");
            Require(receipt["schema"] is int && (int)receipt["schema"] == 1, "Invalid previous receipt");
            string recordedVersion = Text(Map(receipt["inventory"]), "version");
            previous = InventoryFiles(Map(receipt["inventory"]), recordedVersion, game);
            previousOwned = Owned(receipt["owned"], previous);
            if (recordedVersion != installed) previousOwned.Clear();
        }
        var candidates = new HashSet<string>(previousOwned, StringComparer.Ordinal);
        foreach (var pair in files) if (Text(pair.Value, "kind") == "code" || Text(pair.Value, "kind") == "dependency") candidates.Add(pair.Key);
        Require(new HashSet<string>(candidates, StringComparer.OrdinalIgnoreCase).Count == candidates.Count, "Case collision across inventories");
        var observed = new HashSet<string>(StringComparer.Ordinal);
        var nextOwned = new HashSet<string>(StringComparer.Ordinal);
        foreach (object raw in Items(ticket["operations"]))
        {
            var item = Map(raw); Keys(item, "path", "action", "before", "after");
            string path = Relative(Text(item, "path")), action = Text(item, "action"); Sig(item["before"]); Sig(item["after"]);
            Require(candidates.Contains(path) && observed.Add(path), "Unexpected operation");
            Dictionary<string, object> after = files.ContainsKey(path) ? EntrySig(files[path]) : null;
            object before = previousOwned.Contains(path) ? EntrySig(previous[path]) : null;
            string expected;
            if (after == null) expected = EqualSig(item["before"], before) ? "remove" : "keep_unowned";
            else if (EqualSig(item["before"], after)) expected = "keep";
            else if (item["before"] == null) expected = "install";
            else if (before != null && EqualSig(item["before"], before)) expected = "replace";
            else if (before == null && Text(files[path], "kind") == "code") expected = "replace";
            else { Require(false, "Conflicting dependency or modified owned code"); expected = "conflict"; }
            Require(action == expected && EqualSig(item["after"], after), "Operation differs from inventory");
            if (after != null && (action == "install" || action == "replace" || previousOwned.Contains(path))) nextOwned.Add(path);
            if (path == "mods/" + game + "/Driftkings.wotmod") Require(EqualSig(item["before"], installedSig), "Installed code mismatch");
        }
        Require(observed.SetEquals(candidates) && nextOwned.SetEquals(Owned(ticket["owned"], files)), "Ownership plan differs");
    }

    static byte[] ReadMember(ZipArchiveEntry entry, Dictionary<string, object> expected)
    {
        Require(entry != null && entry.Length == Size(expected), "Archive member size differs");
        using (var output = new MemoryStream())
        using (var input = entry.Open())
        {
            byte[] buffer = new byte[65536]; int count;
            while ((count = input.Read(buffer, 0, buffer.Length)) > 0)
            {
                Require(output.Length + count <= Size(expected), "Archive member exceeds limit"); output.Write(buffer, 0, count);
            }
            Require(output.Length == Size(expected) && Hash(output) == Digest(expected), "Archive member hash differs");
            return output.ToArray();
        }
    }

    static void ValidateDistribution(Stream ready, Dictionary<string, object> ticket)
    {
        var inventory = Map(ticket["inventory"]);
        var files = InventoryFiles(inventory, Text(ticket, "version"), Text(ticket, "gameVersion"));
        ready.Position = 0;
        using (var zip = new ZipArchive(ready, ZipArchiveMode.Read, true))
        {
            Require(zip.Entries.Count == files.Count, "Archive inventory differs");
            var seen = new HashSet<string>(StringComparer.OrdinalIgnoreCase);
            foreach (var entry in zip.Entries)
            {
                Require(files.ContainsKey(entry.FullName) && seen.Add(entry.FullName), "Unexpected archive member");
                var item = files[entry.FullName]; byte[] bytes = ReadMember(entry, item);
                if (Text(item, "kind") == "code") using (var code = new MemoryStream(bytes)) Package(code, Text(ticket, "version"));
                if (Text(item, "kind") == "defaults")
                using (var source = new MemoryStream(bytes))
                using (var defaults = new ZipArchive(source, ZipArchiveMode.Read))
                {
                    var expected = new Dictionary<string, Dictionary<string, object>>(StringComparer.Ordinal);
                    foreach (object raw in Items(inventory["defaults"])) { var config = Map(raw); expected.Add(Text(config, "path"), config); }
                    Require(defaults.Entries.Count == expected.Count, "Default inventory differs");
                    var names = new HashSet<string>(StringComparer.OrdinalIgnoreCase);
                    foreach (var config in defaults.Entries)
                    {
                        Require(expected.ContainsKey(config.FullName) && names.Add(config.FullName), "Unexpected default");
                        ReadMember(config, expected[config.FullName]);
                    }
                }
            }
        }
    }

    sealed class Change
    {
        internal string Target, Backup, Temporary, Member;
        internal object Before, After;
        internal byte[] Bytes;
    }

    static void AtomicJson(string path, object value)
    {
        Safe(path, false); string temporary = path + ".tmp"; Safe(temporary, false);
        byte[] bytes = Encoding.UTF8.GetBytes(Json.Serialize(value)); Require(bytes.Length <= 65536, "JSON exceeds limit");
        using (var output = new FileStream(temporary, FileMode.Create, FileAccess.Write, FileShare.None))
        { output.Write(bytes, 0, bytes.Length); output.Flush(true); }
        if (File.Exists(path)) File.Replace(temporary, path, null); else File.Move(temporary, path);
    }

    static Dictionary<string, object> ByteSig(byte[] bytes)
    {
        using (var input = new MemoryStream(bytes)) return new Dictionary<string, object> { { "size", bytes.Length }, { "sha256", Hash(input) } };
    }

    static List<Change> Changes(string root, Dictionary<string, object> ticket)
    {
        var result = new List<Change>();
        foreach (object raw in Items(ticket["operations"]))
        {
            var item = Map(raw); string action = Text(item, "action");
            if (action == "keep" || action == "keep_unowned") continue;
            result.Add(new Change { Target = Path.Combine(root, Text(item, "path").Replace('/', Path.DirectorySeparatorChar)),
                                    Member = Text(item, "path"), Before = item["before"], After = item["after"] });
        }
        byte[] receipt = Encoding.UTF8.GetBytes(Json.Serialize(new { schema = 1, inventory = ticket["inventory"], owned = ticket["owned"] }));
        Require(receipt.Length <= 65536, "Ownership receipt exceeds limit");
        byte[] previous = ticket["previousReceipt"] == null ? null : Encoding.UTF8.GetBytes(Text(ticket, "previousReceipt"));
        result.Add(new Change { Target = Path.Combine(root, "mods", "configs", "Driftkings", "cache", "update", "ownership." + Text(ticket, "gameVersion") + ".json"),
                                Before = previous == null ? null : ByteSig(previous), After = ByteSig(receipt), Bytes = receipt });
        for (int index = 0; index < result.Count; index++)
        {
            result[index].Backup = Path.Combine(stage, "backup-" + index);
            result[index].Temporary = Path.Combine(stage, "new-" + index);
            Safe(result[index].Target, false); Safe(result[index].Backup, false); Safe(result[index].Temporary, false);
        }
        return result;
    }

    static void VerifyKept(string root, Dictionary<string, object> ticket)
    {
        foreach (object raw in Items(ticket["operations"]))
        {
            var item = Map(raw); string action = Text(item, "action");
            if (action == "keep")
                Require(MatchSig(Path.Combine(root, Text(item, "path").Replace('/', Path.DirectorySeparatorChar)), item["before"]), "Shared/kept file changed");
        }
    }

    static void Rollback(List<Change> changes)
    {
        // Validate the whole rollback before modifying any file. Unexpected
        // bytes are retained for diagnosis rather than overwritten or removed.
        foreach (var change in changes)
        {
            Safe(change.Backup, false); Safe(change.Target, false);
            if (File.Exists(change.Backup))
                Require(change.Before != null && MatchSig(change.Backup, change.Before) &&
                        (!File.Exists(change.Target) || MatchSig(change.Target, change.After)), "Ambiguous rollback backup/target");
            else Require(MatchSig(change.Target, change.Before) || change.Before == null && MatchSig(change.Target, change.After), "Ambiguous rollback target");
        }
        for (int index = changes.Count - 1; index >= 0; index--)
        {
            var change = changes[index]; NoGame(); Safe(change.Target, false); Safe(change.Backup, false);
            if (File.Exists(change.Backup))
            {
                if (File.Exists(change.Target)) File.Replace(change.Backup, change.Target, null);
                else File.Move(change.Backup, change.Target);
            }
            else if (change.Before == null && File.Exists(change.Target)) File.Delete(change.Target);
            Require(MatchSig(change.Target, change.Before), "Rollback verification failed");
        }
    }

    static int ApplyModpack(string root, Dictionary<string, object> ticket, Stream ready)
    {
        ValidateModpackTicket(ticket); NoGame();
        var changes = Changes(root, ticket);
        string journal = Path.Combine(stage, "journal.json"); Safe(journal, false);
        string ticketHash; using (var input = File.OpenRead(Path.Combine(stage, "install.json"))) ticketHash = Hash(input);
        if (File.Exists(journal))
        {
            Require(new FileInfo(journal).Length <= 65536, "Journal exceeds limit");
            var state = Json.Deserialize<Dictionary<string, object>>(File.ReadAllText(journal, Encoding.UTF8));
            Keys(state, "schema", "ticketSha256", "status");
            Require(state["schema"] is int && (int)state["schema"] == 1 && Text(state, "ticketSha256") == ticketHash, "Journal belongs to another ticket");
            if (Text(state, "status") == "committed")
            {
                foreach (var change in changes) Require(MatchSig(change.Target, change.After), "Committed file changed");
                VerifyKept(root, ticket); Result("installed", null); return 0;
            }
            if (Text(state, "status") == "applying")
            {
                Rollback(changes); AtomicJson(journal, new { schema = 1, ticketSha256 = ticketHash, status = "rolledBack" });
                Result("rolledBack", "interruptedInstall"); return 2;
            }
            Require(Text(state, "status") == "rolledBack", "Unknown journal state");
        }
        foreach (var change in changes)
        {
            Require(MatchSig(change.Target, change.Before) && !File.Exists(change.Backup), "Installed file changed or unresolved backup");
            Safe(Path.GetDirectoryName(change.Target), true);
        }
        VerifyKept(root, ticket);
        string oldCode = Path.Combine(root, "mods", Text(ticket, "gameVersion"), "Driftkings.wotmod");
        using (var code = File.OpenRead(oldCode)) Package(code, Text(ticket, "installedVersion"));
        // A journal precedes even temporary creation. After a crash all target
        // states can be inferred from recorded before/after hashes and backups.
        AtomicJson(journal, new { schema = 1, ticketSha256 = ticketHash, status = "applying" });
        bool committed = false;
        try
        {
            ready.Position = 0;
            using (var zip = new ZipArchive(ready, ZipArchiveMode.Read, true))
            foreach (var change in changes)
            {
                if (change.After == null) continue;
                Safe(change.Temporary, false);
                // A stale partial belongs to this journal only; backup bytes
                // are never deleted here.
                if (File.Exists(change.Temporary)) File.Delete(change.Temporary);
                byte[] bytes = change.Bytes ?? ReadMember(zip.GetEntry(change.Member), Map(change.After));
                using (var output = new FileStream(change.Temporary, FileMode.CreateNew, FileAccess.Write, FileShare.None))
                { output.Write(bytes, 0, bytes.Length); output.Flush(true); }
                Require(MatchSig(change.Temporary, change.After), "Prepared file hash differs");
            }
            Result("installing", null);
            foreach (var change in changes)
            {
                NoGame(); Safe(change.Target, false); Safe(change.Backup, false); Safe(change.Temporary, false);
                Require(MatchSig(change.Target, change.Before), "Installed file changed during preparation");
                if (change.After == null) File.Move(change.Target, change.Backup);
                else if (change.Before == null) File.Move(change.Temporary, change.Target);
                else File.Replace(change.Temporary, change.Target, change.Backup);
                Require(MatchSig(change.Target, change.After), "Installed file hash differs");
            }
            VerifyKept(root, ticket);
            foreach (var change in changes) Require(MatchSig(change.Target, change.After), "Final verification failed");
            AtomicJson(journal, new { schema = 1, ticketSha256 = ticketHash, status = "committed" }); committed = true;
            Result("installed", null);
        }
        catch
        {
            if (!committed)
            {
                Rollback(changes); AtomicJson(journal, new { schema = 1, ticketSha256 = ticketHash, status = "rolledBack" });
                Result("rolledBack", "installFailed");
            }
            throw;
        }
        // Keep backups for the next-start proof and diagnosis. They are bounded
        // to this transaction and never swept by filename patterns.
        return 0;
    }
}
