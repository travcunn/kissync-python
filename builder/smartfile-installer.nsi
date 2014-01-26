!include "MUI.nsh"
!include "nsProcess.nsh"
SetCompressor lzma

!define PRODUCT_NAME "SmartFile Sync"
!define PRODUCT_VERSION "0.24"
!define PRODUCT_SIMPLENAME "SmartFile Sync"
!define PRODUCT_PUBLISHER "Travis Cunningham"
!define PRODUCT_WEB_SITE "http://www.kissync.com/"
!define PRODUCT_DIR_REGKEY "Software\Microsoft\Windows\CurrentVersion\App Paths\${PRODUCT_NAME}\SmartFile.exe"
!define PRODUCT_UNINST_KEY "Software\Microsoft\Windows\CurrentVersion\Uninstall\${PRODUCT_NAME}"
!define PRODUCT_UNINST_ROOT_KEY "HKLM"
!define MUI_ABORTWARNING
!define MUI_ICON "..\ui\images\icon.ico"
!define MUI_UNICON "..\ui\images\icon.ico"
!define MUI_WELCOMEFINISHPAGE_BITMAP "..\builder\installer.bmp"
!define MUI_COMPONENTSPAGE_SMALLDESC
!define MUI_FINISHPAGE_RUN "$INSTDIR\SmartFile.exe"
!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_COMPONENTS
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH
!insertmacro MUI_UNPAGE_COMPONENTS
!insertmacro MUI_UNPAGE_INSTFILES
!insertmacro MUI_LANGUAGE "English"
!insertmacro MUI_RESERVEFILE_INSTALLOPTIONS

Name "${PRODUCT_NAME} ${PRODUCT_VERSION}"
OutFile "smartfile-installer.exe"
InstallDir "$PROGRAMFILES\${PRODUCT_NAME}"
InstallDirRegKey HKLM "${PRODUCT_DIR_REGKEY}" ""
ShowInstDetails show
ShowUnInstDetails show

Section "!SmartFile (Required)" INSTALL_SMARTFILE
  SectionIn 1 RO
  SetOutPath "$INSTDIR"
  ${nsProcess::KillProcess} "SmartFile.exe" $R4
  File "icon.ico"
  File "_ctypes.pyd"
  File "_hashlib.pyd"
  File "_multiprocessing.pyd"
  File "_socket.pyd"
  File "_ssl.pyd"
  File "API-MS-Win-Core-LocalRegistry-L1-1-0.dll"
  File "bz2.pyd"
  File "cacert.pem"
  File "SmartFile.exe"
  File "library.zip"
  File "MPR.dll"
  File "pyexpat.pyd"
  File "PySide.QtCore.pyd"
  File "PySide.QtGui.pyd"
  File "PySide.QtNetwork.pyd"
  File "PySide.QtWebKit.pyd"
  File "pyside-python2.7.dll"
  File "python27.dll"
  File "pywintypes27.dll"
  File "QtCore4.dll"
  File "QtGui4.dll"
  File "QtNetwork4.dll"
  File "QtWebKit4.dll"
  File "select.pyd"
  File "shiboken-python2.7.dll"
  File "unicodedata.pyd"
  File "w9xpopen.exe"
  File "win32api.pyd"
  File "win32pipe.pyd"
  File "win32wnet.pyd"
  File "libeay32.dll"
  File "ssleay32.dll"
  SetOutPath "$INSTDIR\imageformats"
  file "imageformats\qico4.dll"
  file "imageformats\qjpeg4.dll"
  CreateDirectory "$SMPROGRAMS\${PRODUCT_NAME}"
  CreateShortCut "$SMPROGRAMS\${PRODUCT_NAME}\SmartFile.lnk" "$INSTDIR\SmartFile.exe"
  CreateShortCut "$SMSTARTUP\SmartFile.lnk" "$INSTDIR\SmartFile.exe"
SectionEnd

Section -AdditionalIcons
  CreateShortCut "$SMPROGRAMS\${PRODUCT_NAME}\Uninstall.lnk" "$INSTDIR\uninst.exe"
SectionEnd

Section -Post
  WriteUninstaller "$INSTDIR\uninst.exe"
  WriteRegStr HKLM "${PRODUCT_DIR_REGKEY}" "" "$INSTDIR\SmartFile.exe"
  WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "DisplayName" "$(^Name)"
  WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "UninstallString" "$INSTDIR\uninst.exe"
  WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "DisplayIcon" "$INSTDIR\SmartFile.exe"
  WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "DisplayVersion" "${PRODUCT_VERSION}"
  WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "URLInfoAbout" "${PRODUCT_WEB_SITE}"
  WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "Publisher" "${PRODUCT_PUBLISHER}"
SectionEnd

!insertmacro MUI_FUNCTION_DESCRIPTION_BEGIN
  !insertmacro MUI_DESCRIPTION_TEXT ${INSTALL_SMARTFILE} "SmartFile Desktop Sync"
!insertmacro MUI_FUNCTION_DESCRIPTION_END


Section "un.SmartFile" UNINSTALL_SMARTFILE
  SectionIn 1 RO
  Delete "$INSTDIR\_ctypes.pyd"
  Delete "$INSTDIR\_hashlib.pyd"
  Delete "$INSTDIR\_multiprocessing.pyd"
  Delete "$INSTDIR\_socket.pyd"
  Delete "$INSTDIR\_ssl.pyd"
  Delete "$INSTDIR\API-MS-Win-Core-LocalRegistry-L1-1-0.dll"
  Delete "$INSTDIR\bz2.pyd"
  Delete "$INSTDIR\cacert.pem"
  Delete "$INSTDIR\SmartFile.exe"
  Delete "$INSTDIR\SmartFile.exe.log"
  Delete "$INSTDIR\library.zip"
  Delete "$INSTDIR\MPR.dll"
  Delete "$INSTDIR\pyexpat.pyd"
  Delete "$INSTDIR\PySide.QtCore.pyd"
  Delete "$INSTDIR\PySide.QtGui.pyd"
  Delete "$INSTDIR\PySide.QtNetwork.pyd"
  Delete "$INSTDIR\PySide.QtWebKit.pyd"
  Delete "$INSTDIR\pyside-python2.7.dll"
  Delete "$INSTDIR\python27.dll"
  Delete "$INSTDIR\pywintypes27.dll"
  Delete "$INSTDIR\QtCore4.dll"
  Delete "$INSTDIR\QtGui4.dll"
  Delete "$INSTDIR\QtNetwork4.dll"
  Delete "$INSTDIR\QtWebKit4.dll"
  Delete "$INSTDIR\select.pyd"
  Delete "$INSTDIR\shiboken-python2.7.dll"
  Delete "$INSTDIR\unicodedata.pyd"
  Delete "$INSTDIR\w9xpopen.exe"
  Delete "$INSTDIR\win32api.pyd"
  Delete "$INSTDIR\win32pipe.pyd"
  Delete "$INSTDIR\win32wnet.pyd"
  Delete "$INSTDIR\imageformats\qico4.dll"
  Delete "$INSTDIR\imageformats\qjpeg4.dll"
  Delete "$INSTDIR\uninst.exe"
  RMDir "$INSTDIR\imageformats"
  RMDir "$INSTDIR"
  Delete "$SMPROGRAMS\${PRODUCT_NAME}\Uninstall.lnk"
  Delete "$SMPROGRAMS\${PRODUCT_NAME}\SmartFile.lnk"
  RMDir "$SMPROGRAMS\${PRODUCT_NAME}"
  Delete "$SMSTARTUP\SmartFile.lnk"
  DeleteRegKey ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}"
  DeleteRegKey HKLM "${PRODUCT_DIR_REGKEY}"
SectionEnd

!insertmacro MUI_UNFUNCTION_DESCRIPTION_BEGIN
  !insertmacro MUI_DESCRIPTION_TEXT ${UNINSTALL_SMARTFILE} "Uninstalls SmartFile Sync from your computer."
!insertmacro MUI_UNFUNCTION_DESCRIPTION_END
