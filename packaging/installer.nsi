; CamFilter Recorder — NSIS Installer Script
; Author : Lowil Ray Delos Reyes
; Version: 1.3.0

!define APP_NAME        "CamFilter Recorder"
!define APP_VERSION     "1.3.0"
!define APP_PUBLISHER   "Lowil Ray Delos Reyes"
!define APP_EXE         "CamFilterRecorder.exe"
!define APP_DIR         "CamFilterRecorder"
!define INSTALL_DIR     "$PROGRAMFILES64\${APP_NAME}"
!define UNINSTALL_KEY   "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}"

Name              "${APP_NAME} ${APP_VERSION}"
OutFile           "CamFilterRecorder-Setup.exe"
InstallDir        "${INSTALL_DIR}"
InstallDirRegKey  HKLM "${UNINSTALL_KEY}" "InstallLocation"
RequestExecutionLevel admin
SetCompressor     /SOLID lzma

!include "MUI2.nsh"

; MUI Pages
!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_LICENSE "..\LICENSE.txt"
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH

!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES

!insertmacro MUI_LANGUAGE "English"

; ── Upgrade detection ───────────────────────────────────────────────────────
; On startup, check whether a previous version is already installed.
; If so, offer to uninstall it first so the new version installs cleanly.
Function .onInit
  ReadRegStr $R0 HKLM "${UNINSTALL_KEY}" "UninstallString"
  StrCmp $R0 "" done          ; nothing installed → continue normally

  ReadRegStr $R1 HKLM "${UNINSTALL_KEY}" "DisplayVersion"

  MessageBox MB_OKCANCEL|MB_ICONQUESTION \
    "${APP_NAME} $R1 is already installed.$\n$\n\
Click OK to remove it and install ${APP_NAME} ${APP_VERSION}.$\n\
Click Cancel to exit." \
    IDOK do_uninstall
  Abort                       ; user cancelled

do_uninstall:
  ; Run the existing uninstaller silently, keeping the install directory
  ; so we can overwrite it in the very next step.
  ExecWait '"$R0" /S _?=$INSTDIR'

  ; If the uninstaller binary itself is still there (e.g. couldn't self-delete),
  ; remove it so the fresh install can write a clean copy.
  IfFileExists "$INSTDIR\Uninstall.exe" 0 done
  Delete "$INSTDIR\Uninstall.exe"

done:
FunctionEnd

; ── Installer ──────────────────────────────────────────────────────────────
Section "CamFilter Recorder" SecMain
  SectionIn RO
  SetOutPath "$INSTDIR"

  ; Copy all PyInstaller --onedir output
  File /r "..\dist\${APP_DIR}\*"

  ; Write uninstall info to registry
  WriteRegStr   HKLM "${UNINSTALL_KEY}" "DisplayName"      "${APP_NAME}"
  WriteRegStr   HKLM "${UNINSTALL_KEY}" "DisplayVersion"   "${APP_VERSION}"
  WriteRegStr   HKLM "${UNINSTALL_KEY}" "Publisher"        "${APP_PUBLISHER}"
  WriteRegStr   HKLM "${UNINSTALL_KEY}" "InstallLocation"  "$INSTDIR"
  WriteRegStr   HKLM "${UNINSTALL_KEY}" "UninstallString"  "$INSTDIR\Uninstall.exe"
  WriteRegDWORD HKLM "${UNINSTALL_KEY}" "NoModify"         1
  WriteRegDWORD HKLM "${UNINSTALL_KEY}" "NoRepair"         1

  WriteUninstaller "$INSTDIR\Uninstall.exe"

  ; Start Menu shortcut
  CreateDirectory "$SMPROGRAMS\${APP_NAME}"
  CreateShortcut  "$SMPROGRAMS\${APP_NAME}\${APP_NAME}.lnk"   "$INSTDIR\${APP_EXE}"
  CreateShortcut  "$SMPROGRAMS\${APP_NAME}\Uninstall.lnk"     "$INSTDIR\Uninstall.exe"

  ; Desktop shortcut
  CreateShortcut  "$DESKTOP\${APP_NAME}.lnk" "$INSTDIR\${APP_EXE}"
SectionEnd

; ── Uninstaller ─────────────────────────────────────────────────────────────
Section "Uninstall"
  RMDir /r "$INSTDIR"
  Delete "$DESKTOP\${APP_NAME}.lnk"
  RMDir /r "$SMPROGRAMS\${APP_NAME}"
  DeleteRegKey HKLM "${UNINSTALL_KEY}"
SectionEnd
