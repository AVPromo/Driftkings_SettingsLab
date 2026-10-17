// Relaunch only after all already scheduled local installers release their gates.
using System;
using System.IO;
using System.Threading;

internal static class ExitWork
{
    internal static void Wait(string root, Action<string> safe) {
        foreach (string name in new string[] { "fog", "update" }) {
            string gate = Path.Combine(root, "mods", "configs", "Driftkings", "cache", name, "install.lock");
            DateTime deadline = DateTime.UtcNow.AddMinutes(2);
            while (true) {
                safe(gate);
                if (!File.Exists(gate)) break;
                try {
                    using (var handle = new FileStream(gate, FileMode.Open, FileAccess.ReadWrite, FileShare.None)) { }
                    break;
                } catch (IOException) {
                    if (DateTime.UtcNow >= deadline) throw new IOException("Timed out waiting for " + name + " installer");
                    Thread.Sleep(100);
                }
            }
        }
    }
}
