# Intelligent-Lab-PM-300-100-Documentation
Documentation of the menus and other documentation of the PM series of scales from Intelligent Lab, explicitly testing on the PM-300

## Existing Documentation
### Videos
-  [Intellegent Lab Youtube's PM results](https://www.youtube.com/@intelligentwt/search?query=PM)

### PDFs
-  [Intellegent Lab Youtube's PM Series Manual](https://drive.google.com/drive/folders/1ow5p9J6DdfnqKT-o0nRZ4C1rdYtlJJHq)
-  [Official Brochure](https://cdn.bullseyescale.com/wp-content/uploads/2020/01/pm-series-lab-balance-brochure-2021.pdf)
-  [Old model w/o IR Manual (2010)](https://res.cloudinary.com/iwh/image/upload/q_auto%2Cg_center/assets/1/26/pmanalytical-usermanual.pdf)
-  [Generic scale (similar) Manual](https://www.wantbalance.com/uploadfiles/128.1.164.27/webid1958/Downloadfile/202203/6226bd9d66951.pdf)
-  [Broken link to manual (from QR code on device)](http://www.intelligentwt.com/v/vspfiles/files/pdf/PM_Balance_Calibration_Instructions.pdf)

## New Documentation
So far I've been able to produce this state diagram:
```mermaid
stateDiagram-v2
    [*] --> PowerOff

    PowerOff --> BootNormal: Power on
    PowerOff --> StartupSettings: Hold CAL + power on
    PowerOff --> HiddenConfig: Hold CAL + BL + power on

    BootNormal --> WeighingMode: Startup complete

    WeighingMode --> StandardCalibration: Hold CAL about 3 s
    WeighingMode --> PrintMenu: MODE path to Prt
    WeighingMode --> IROffShortcut: CAL + TARE
    WeighingMode --> AltMeasurementState: CAL + BL in regular mode
    AltMeasurementState --> WeighingMode: CAL + BL again

    note right of WeighingMode
      Least-bad observed state:
      empty 0.000
      100 g -> about 49.976 g
    end note

    note right of AltMeasurementState
      Alternate internal state:
      empty about 285.668 g
      100 g -> about 847.976 g
    end note

    state StandardCalibration {
        [*] --> CalPrompt
        ApplyMass --> CalResult: Display CAL then value
        CalPrompt --> ApplyMass: Prompted mass observed = 100 g
        CalResult --> [*]
    }

    state PrintMenu {
        [*] --> PrintSelect
        PrintSelect --> Hand: hAnd
        PrintSelect --> Auto: AUto
        PrintSelect --> Contin: Contin
    }

    state StartupSettings {
        [*] --> ZeroTracking
        ZeroTracking --> AutoTare: CAL
        AutoTare --> [*]: BL confirm or exit
    }

    note right of ZeroTracking
      -Zero-
      TARE changes 0..5
    end note

    note right of AutoTare
      -tArE-
      TARE changes 0..9
    end note

    state HiddenConfig {
        [*] --> PageCycle
        PageCycle --> IRSelect: ir-SEL
        PageCycle --> CalDB: cal-db
        PageCycle --> OtherEditablePages: other pages
        IRSelect --> PageCycle
        CalDB --> PageCycle
        OtherEditablePages --> PageCycle
    }

    note right of HiddenConfig
      CAL cycles pages
      MODE edits values
      TARE edits values
      BL exits to weighing mode
    end note

    state IROffShortcut {
        [*] --> IRForcedOff
    }

    note right of IROffShortcut
      CAL + TARE in regular mode
      turns IR off
    end note

    state "?" as MysteryIsland
    note right of MysteryIsland
      Earlier conflicting startup behavior
      still unresolved
    end note
    ```
