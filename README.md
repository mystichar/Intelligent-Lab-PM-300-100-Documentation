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
Generally speaking, MODE is a 'next' button, whereas TARE is often a 'select' button. The only time this isnt the case is when in the hidden Cal-db mode which is in the menu open by holding CAL and BL on startup.

In that mode, TARE cycles through the 10s place and MODE cycles through the 100s place.

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

### Serial
On startup, if contin(uous) output is disabled, it issues a HEX 00, or . symbol

During calibration, it continues to print the last weight until its done, which is probably around 0.
In some menus, the weight printed changes to `+0000000. g  ..`
It doesnt seem to provide an debugging serial output.

### Internals
It has what appears to be a 2-layer PCB, marked X243476A, with unused through holes areas:
- TO DISPLAY
- CAL, which is effectively a soldered on dip switch between ON and OFF mode ( mine soldered to ON)
- and one unlabelled 2 x 8 connector likely for calibration/debugging
- an unused 4-pin LED spot on the front
- 2 pins labeled A and B, labeled RS485

Other features of note are two potentiometers labeled V1 and V2 on the backside. Also D4 is shorted instead of a diode.

Chips:
- U8: BL55066; 1528 YH; CCG 5231K, with 10  pins on all 4 sides 0.75mm pitch
- U6: BL24C02; with 2 sets of 4 pins 1mm pitch
- U7: 078F0513A; 1722EM421, with the same package as U8
- U5: CIRRUS; C555328SZ; DXYD1743, with 2 sides with 10 pins and maybe a 0.5mm pitch
- U9: SIPEX SP232EEN; 813LT0521 with two sets of 8 pins, and the top right most pin cut off (perhaps a write enable? or just broken?) 1mm pitch
- U4: LM393; PGDA, with two sets of 4 pins with a 1mm pitch

The load cell is a MSP3-450h, labeled Emin=10g, Vmin=0.1g; www.lwbmt.com
