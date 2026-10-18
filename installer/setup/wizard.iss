// All component names, paths and option keys come from the generated include.
var
  ResetConfig, PreserveProfile: Boolean;
  Preview: TBitmapImage;
  Description, PreserveNotice: TNewStaticText;

function ConfigRoot: String;
begin
  Result := ExpandConstant('{app}\mods\configs\Driftkings');
end;

function IsReparseDirectory(const Folder: String): Boolean;
var
  Item: TFindRec;
begin
  Result := False;
  if FindFirst(Folder, Item) then begin
    Result := (Item.Attributes and $400) <> 0;
    FindClose(Item);
  end;
end;

function ConfigurationPathError: String;
var
  Folder: String;
begin
  Result := '';
  if IsReparseDirectory(ConfigRoot + '\installer-backup') then begin
    Result := 'Installer backup path uses a reparse point';
    Exit;
  end;
  Folder := ConfigRoot;
  while CompareText(Folder, ExpandConstant('{app}')) <> 0 do begin
    if IsReparseDirectory(Folder) then begin
      Result := 'Configuration path uses a reparse point: ' + Folder;
      Exit;
    end;
    Folder := ExtractFileDir(Folder);
  end;
end;

function HasProfile: Boolean;
var
  Item, Child: TFindRec;
begin
  Result := FileExists(ConfigRoot + '\load.json') or
    FileExists(ConfigRoot + '\load.json.previous') or
    FileExists(ConfigRoot + '\Driftkings.json') or DirExists(ConfigRoot + '\default');
  if Result then Exit;
  if FindFirst(ConfigRoot + '\*.json', Item) then begin
    Result := True;
    FindClose(Item);
    Exit;
  end;
  if not FindFirst(ConfigRoot + '\*', Item) then Exit;
  try
    repeat
      if ((Item.Attributes and FILE_ATTRIBUTE_DIRECTORY) <> 0) and
         (Item.Name <> '.') and (Item.Name <> '..') and
         (CompareText(Item.Name, 'cache') <> 0) and (CompareText(Item.Name, 'installer-backup') <> 0) and
         (CompareText(Item.Name, 'installer') <> 0) and (CompareText(Item.Name, 'SixthSense') <> 0) and
         (CompareText(Item.Name, 'images') <> 0) then
        if FindFirst(ConfigRoot + '\' + Item.Name + '\*.json', Child) then begin
          Result := True;
          FindClose(Child);
        end;
    until Result or not FindNext(Item);
  finally
    FindClose(Item);
  end;
end;

procedure UpdatePreview(Sender: TObject);
var
  Index, AvailableWidth, AvailableHeight, Width, Height: Integer;
  Filename: String;
begin
  Preview.Visible := False;
  Index := WizardForm.ComponentsList.ItemIndex;
  Description.Caption := '';
  if (Index < 0) or (Index >= PreviewCount) then Exit;
  Description.Caption := CustomMessage(PreviewMessage(Index));
  Filename := PreviewFile(Index);
  if Filename = '' then Exit;
  try
    ExtractTemporaryFile(Filename);
    Preview.PngImage.LoadFromFile(ExpandConstant('{tmp}\') + Filename);
    AvailableWidth := WizardForm.SelectComponentsPage.ClientWidth - Preview.Left;
    AvailableHeight := WizardForm.ComponentsList.Height - Description.Height - ScaleY(12);
    Width := AvailableWidth;
    Height := Preview.PngImage.Height * Width div Preview.PngImage.Width;
    if Height > AvailableHeight then begin
      Height := AvailableHeight;
      Width := Preview.PngImage.Width * Height div Preview.PngImage.Height;
    end;
    Preview.Width := Width;
    Preview.Height := Height;
    Preview.Visible := True;
  except
    Log('Optional preview unavailable: ' + Filename);
  end;
end;

procedure PreviewKeyUp(Sender: TObject; var Key: Word; Shift: TShiftState);
begin
  UpdatePreview(Sender);
end;

procedure InitializeWizard;
begin
  ResetConfig := ExpandConstant('{param:RESETCONFIG|0}') = '1';
  WizardForm.ComponentsList.Width := WizardForm.ComponentsList.Width * 3 div 5;
  Description := TNewStaticText.Create(WizardForm);
  Description.Parent := WizardForm.SelectComponentsPage;
  Description.Left := WizardForm.ComponentsList.Left + WizardForm.ComponentsList.Width + ScaleX(12);
  Description.Top := WizardForm.ComponentsList.Top;
  Description.Width := WizardForm.SelectComponentsPage.ClientWidth - Description.Left;
  Description.Height := ScaleY(70);
  Description.AutoSize := False;
  Description.WordWrap := True;
  Preview := TBitmapImage.Create(WizardForm);
  Preview.Parent := WizardForm.SelectComponentsPage;
  Preview.Left := Description.Left;
  Preview.Top := Description.Top + Description.Height + ScaleY(12);
  Preview.Stretch := True;
  Preview.Visible := False;
  WizardForm.ComponentsList.OnClick := @UpdatePreview;
  WizardForm.ComponentsList.OnClickCheck := @UpdatePreview;
  WizardForm.ComponentsList.OnKeyUp := @PreviewKeyUp;
  PreserveNotice := TNewStaticText.Create(WizardForm);
  PreserveNotice.Parent := WizardForm.SelectDirPage;
  PreserveNotice.Left := WizardForm.DirEdit.Left;
  PreserveNotice.Top := WizardForm.DirEdit.Top + WizardForm.DirEdit.Height + ScaleY(20);
  PreserveNotice.Width := WizardForm.SelectDirPage.ClientWidth - PreserveNotice.Left;
  PreserveNotice.Height := ScaleY(55);
  PreserveNotice.AutoSize := False;
  PreserveNotice.WordWrap := True;
  PreserveNotice.Caption := CustomMessage('PreserveSettings');
  PreserveNotice.Visible := False;
end;

procedure CurPageChanged(CurPageID: Integer);
begin
  if CurPageID = wpSelectComponents then UpdatePreview(WizardForm.ComponentsList);
  PreserveNotice.Visible := HasProfile and not ResetConfig;
end;

function ShouldSkipPage(PageID: Integer): Boolean;
begin
  Result := ((PageID = wpSelectComponents) or (PageID = wpSelectTasks)) and HasProfile and not ResetConfig;
end;

function XmlValue(const Data, Name: String): String;
var
  Start, Finish: Integer;
begin
  Result := '';
  Start := Pos('<' + Name + '>', Data);
  Finish := Pos('</' + Name + '>', Data);
  if (Start > 0) and (Finish > Start) then
    Result := Trim(Copy(Data, Start + Length(Name) + 2, Finish - Start - Length(Name) - 2));
end;

function PrepareToInstall(var NeedsRestart: Boolean): String;
var
  Data: AnsiString;
  Version: String;
  Locator, Services, Processes: Variant;
begin
  Result := CustomMessage('WrongClient');
  if not LoadStringFromFile(ExpandConstant('{app}\version.xml'), Data) then Exit;
  Version := XmlValue(String(Data), 'version');
  if Copy(Version, 1, 2) = 'v.' then Delete(Version, 1, 2);
  if Pos(' #', Version) > 0 then Version := Copy(Version, 1, Pos(' #', Version) - 1);
  if (Version <> '{#GameVersion}') or
     (Pos('|' + Uppercase(XmlValue(String(Data), 'realm')) + '|', '{#SupportedRealms}') = 0) then Exit;
  Result := ExistingDependenciesError;
  if Result <> '' then Exit;
  Result := ConfigurationPathError;
  if Result <> '' then Exit;
  Result := CustomMessage('ProcessCheckFailed');
  try
    Locator := CreateOleObject('WbemScripting.SWbemLocator');
    Services := Locator.ConnectServer('', 'root\cimv2');
    Processes := Services.ExecQuery('SELECT ProcessId FROM Win32_Process WHERE Name = ''WorldOfTanks.exe''');
    if Processes.Count > 0 then begin
      Result := CustomMessage('CloseGame');
      Exit;
    end;
  except
    Exit;
  end;
  PreserveProfile := HasProfile and not ResetConfig;
  Result := '';
end;

procedure CollectConfigs(const Folder, Relative: String; Files: TStringList);
var
  Item: TFindRec;
  Child, Name: String;
begin
  if not FindFirst(AddBackslash(Folder) + '*', Item) then Exit;
  try
    repeat
      Name := Item.Name;
      if (Name <> '.') and (Name <> '..') then begin
        Child := AddBackslash(Relative) + Name;
        if Relative = '' then Child := Name;
        if (Relative <> '') or ((CompareText(Name, 'installer-backup') <> 0) and
           (CompareText(Name, 'cache') <> 0) and (CompareText(Name, 'installer') <> 0) and
           (CompareText(Name, 'images') <> 0) and (CompareText(Name, 'SixthSense') <> 0)) then begin
          if (Item.Attributes and $400) <> 0 then RaiseException('Cannot reset configurations through a reparse point');
          if (Item.Attributes and FILE_ATTRIBUTE_DIRECTORY) <> 0 then
            CollectConfigs(AddBackslash(Folder) + Name, Child, Files)
          else if (CompareText(ExtractFileExt(Name), '.json') = 0) or
                  (Pos('.json.previous', Lowercase(Name)) > 0) or (Pos('.json.bak', Lowercase(Name)) > 0) then
            Files.Add(Child);
        end;
      end;
    until not FindNext(Item);
  finally
    FindClose(Item);
  end;
end;

procedure WriteNewConfig(const Path, Data: String; Created: TStringList);
var
  Temporary: String;
begin
  if FileExists(Path) then RaiseException('Refusing to overwrite configuration: ' + Path);
  if not ForceDirectories(ExtractFileDir(Path)) then RaiseException('Cannot create configuration directory');
  Temporary := Path + '.installer-new';
  if FileExists(Temporary) then RaiseException('A previous installer write is still present');
  if not SaveStringToFile(Temporary, Data + #13#10, False) then RaiseException('Cannot write configuration');
  if not RenameFile(Temporary, Path) then begin
    DeleteFile(Temporary);
    RaiseException('Cannot publish configuration');
  end;
  Created.Add(Path);
end;

function JsonBool(Value: Boolean): String;
begin
  if Value then Result := 'true' else Result := 'false';
end;

procedure WriteChoices(Created: TStringList);
var
  Files: TStringList;
  I, J: Integer;
  Body, Filename: String;
begin
  Files := TStringList.Create;
  try
    for I := 0 to ChoiceCount - 1 do
      if Files.IndexOf(ChoiceFile(I)) < 0 then Files.Add(ChoiceFile(I));
    for I := 0 to Files.Count - 1 do begin
      Body := '';
      Filename := Files[I];
      for J := 0 to ChoiceCount - 1 do
        if (ChoiceFile(J) = Filename) and (ChoiceSelected(J) <> ChoiceDefault(J)) then begin
          if Body <> '' then Body := Body + ',' + #13#10;
          Body := Body + '  "' + ChoiceKey(J) + '": ' + JsonBool(ChoiceSelected(J));
        end;
      if Body <> '' then WriteNewConfig(ConfigRoot + '\' + Filename, '{' + #13#10 + Body + #13#10 + '}', Created);
    end;
    WriteNewConfig(ConfigRoot + '\load.json', '{"loadConfig":"default"}', Created);
    if not ForceDirectories(ConfigRoot + '\default') then RaiseException('Cannot create default profile');
  finally
    Files.Free;
  end;
end;

procedure ApplyConfiguration;
var
  Files, Created: TStringList;
  Backup, Source, Destination: String;
  I, Suffix: Integer;
  Started: Boolean;
begin
  Files := TStringList.Create;
  Created := TStringList.Create;
  Started := False;
  Backup := '';
  try
    try
      if ResetConfig and DirExists(ConfigRoot) then begin
        CollectConfigs(ConfigRoot, '', Files);
        Backup := ConfigRoot + '\installer-backup\' + GetDateTimeString('yyyymmdd-hhnnss', '-', ':');
        Suffix := 0;
        while DirExists(Backup + '-' + IntToStr(Suffix)) do Suffix := Suffix + 1;
        Backup := Backup + '-' + IntToStr(Suffix);
        for I := 0 to Files.Count - 1 do begin
          Source := ConfigRoot + '\' + Files[I];
          Destination := Backup + '\' + Files[I];
          if not ForceDirectories(ExtractFileDir(Destination)) or not CopyFile(Source, Destination, True) then
            RaiseException('Configuration backup failed; originals have not been changed');
        end;
      end;
      Started := True;
      for I := 0 to Files.Count - 1 do
        if not DeleteFile(ConfigRoot + '\' + Files[I]) then RaiseException('Cannot reset configuration');
      WriteChoices(Created);
    except
      if Started then begin
        for I := 0 to Created.Count - 1 do DeleteFile(Created[I]);
        for I := 0 to Files.Count - 1 do
          if not CopyFile(Backup + '\' + Files[I], ConfigRoot + '\' + Files[I], False) then
            Log('Cannot restore configuration; backup retained: ' + Files[I]);
      end;
      RaiseException(GetExceptionMessage);
    end;
  finally
    Created.Free;
    Files.Free;
  end;
end;

procedure WriteMediaReadme(const Folder, Content: String);
var
  Filename: String;
begin
  if IsReparseDirectory(ConfigRoot + '\' + Folder) then begin
    Log('Preserving linked user-media folder without writing a README: ' + Folder);
    Exit;
  end;
  Filename := ConfigRoot + '\' + Folder + '\README.txt';
  if not FileExists(Filename) then
    if not SaveStringToFile(Filename, Content + #13#10, False) then RaiseException('Cannot write user media README');
end;

procedure CurStepChanged(CurStep: TSetupStep);
begin
  if CurStep <> ssPostInstall then Exit;
  VerifyInstalledPayload;
  if not PreserveProfile then ApplyConfiguration;
  WriteMediaReadme('SixthSense', 'Custom Sixth Sense icon: SixthSenseIcon.png. Select it in the Driftkings settings panel. This folder is never removed by the uninstaller.');
  WriteMediaReadme('images', 'Custom overlay images: use mods/configs/Driftkings/images/<filename>.png in the settings panel. This folder is never removed by the uninstaller.');
end;
