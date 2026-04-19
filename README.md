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

    PowerOff --> BootNormal : Power on
    PowerOff --> StartupSettings : Hold CAL + power on
    PowerOff --> HiddenConfig : Hold CAL + BL + power on

    BootNormal --> WeighingMode : Startup complete

    WeighingMode --> StandardCalibration : Hold CAL ~3 s
    WeighingMode --> PrintMenu : MODE path to Prt
    WeighingMode --> IROffShortcut : CAL + TARE
    WeighingMode --> AltMeasurementState : CAL + BL in regular mode
    AltMeasurementState --> WeighingMode : CAL + BL again

    state WeighingMode {
        [*] --> NormalState
        NormalState : Normal weighing screen
        NormalState : Observed least-bad state:
        NormalState : empty 0.000
        NormalState : 100 g -> ~49.976 g
    }

    state AltMeasurementState {
        [*] --> WeirdState
        WeirdState : Alternate internal state
        WeirdState : empty ~285.668 g
        WeirdState : 100 g -> ~847.976 g
    }

    state StandardCalibration {
        [*] --> CalPrompt
        CalPrompt : Hold CAL in regular mode
        CalPrompt : Display prompts required mass
        CalPrompt : Observed prompt: 100 g
        CalPrompt --> ApplyMass : Place prompted mass
        ApplyMass --> CalResult : Display CAL then value
        CalResult : Observed abnormal result:
        CalResult : 100 g -> ~49.997 g
        CalResult --> WeighingMode : Exit / complete
    }

    state PrintMenu {
        [*] --> PrintSelect
        PrintSelect --> Hand : hAnd
        PrintSelect --> Auto : AUto
        PrintSelect --> Contin : Contin? from related manual
        Hand --> WeighingMode : Exit
        Auto --> WeighingMode : Exit
        Contin --> WeighingMode : Exit
    }

    state StartupSettings {
        [*] --> ZeroTracking
        ZeroTracking : -Zero-
        ZeroTracking : TARE changes value 0..5
        ZeroTracking --> AutoTare : CAL
        AutoTare : -tArE-
        AutoTare : TARE changes value 0..9
        AutoTare --> WeighingMode : BL confirm / exit
    }

    state HiddenConfig {
        [*] --> PageCycle
        PageCycle : CAL cycles pages
        PageCycle : MODE edits values
        PageCycle : TARE edits values
        PageCycle --> IRSelect : page = ir-SEL
        PageCycle --> CalDB : page = cal-db
        PageCycle --> OtherEditablePages : other pages not yet mapped

        state IRSelect {
            [*] --> IRToggle
            IRToggle : ON / OFF
        }

        state CalDB {
            [*] --> DBValueEdit
            DBValueEdit : Numeric parameter editing
            DBValueEdit : MODE changes 100s
            DBValueEdit : TARE changes 10s
        }

        OtherEditablePages --> PageCycle
        IRSelect --> PageCycle
        CalDB --> PageCycle
        PageCycle --> WeighingMode : BL exit / enter operation
    }

    state IROffShortcut {
        [*] --> IRForcedOff
        IRForcedOff : CAL + TARE in regular mode
        IRForcedOff : Turns IR off
        IRForcedOff --> WeighingMode
    }

    state "?" as MysteryIsland
    note right of MysteryIsland
        Earlier observed startup behavior conflicted
        with later confirmed paths.
        Possible causes:
        - accidental different key timing
        - firmware state dependency
        - undocumented branch
        - menu alias / shared entry path
    end note
    ```
