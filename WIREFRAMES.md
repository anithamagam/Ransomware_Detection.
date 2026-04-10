# 📐 Wireframes & User Flow
## Android Malware Detection App

> **Quick Reference Guide**  
> **Visual flow diagrams for the UI/UX redesign**

---

## 🔄 Complete User Journey

```
START
  ↓
┌─────────────────┐
│   HOME SCREEN   │ ← User launches app
│                 │
│ • Welcome msg   │
│ • Upload zone   │  
│ • Recent scans  │
│ • Navigation    │
└─────────────────┘
  ↓ (Tap upload/drag file)
┌─────────────────┐
│ FILE SELECTION  │ ← User selects APK
│                 │
│ • File browser  │
│ • File validation│
│ • Batch option │
└─────────────────┘
  ↓ (File confirmed)
┌─────────────────┐
│ LOADING SCREEN  │ ← Processing starts  
│                 │
│ • Progress bar  │
│ • Status updates│
│ • Cancel option │
└─────────────────┘
  ↓ (Analysis complete)
┌─────────────────┐
│ RESULTS SCREEN  │ ← Show findings
│                 │
│ • Risk status   │
│ • Details tabs  │
│ • Action buttons│
└─────────────────┘
  ↓ (User actions)
┌─────────────────┐
│ NEXT ACTIONS    │ ← Post-results
│                 │  
│ • Save report   │
│ • Scan another  │
│ • View history  │
└─────────────────┘
  ↓
END/REPEAT
```

---

## 📱 Screen-by-Screen Breakdown

### 1. Home Screen Layout

```
┌─────────────────────────────────┐ ← Status Bar
│ 🛡️ Malware Detector    [⚙️][ℹ️] │ ← Header (60dp)
├─────────────────────────────────┤
│                                 │
│ 🛡️ Secure Your Android Apps     │ ← Hero Section
│                                 │ 
│ ┌─────────────────────────────┐ │
│ │     📱 DROP APK HERE        │ │ ← Upload Zone
│ │                             │ │   (200dp height)
│ │ Drag & drop or tap to       │ │
│ │ browse files                │ │
│ │                             │ │
│ │ .apk files, max 100MB       │ │
│ └─────────────────────────────┘ │
│                                 │
│ [Browse] [Batch Scan]          │ ← Action Buttons
│                                 │
│ Recent Scans ─────────────────  │ ← History Section
│ 📱 App1.apk    ✅ Safe         │   (CardView list)
│ 🎮 App2.apk    ⚠️ Warning      │
│ 💰 App3.apk    🚨 Threat       │
│                                 │
├─────────────────────────────────┤
│ [🏠] [📊] [⚙️] [ℹ️]           │ ← Bottom Nav (56dp)
└─────────────────────────────────┘
```

### 2. Loading Screen Layout

```
┌─────────────────────────────────┐
│ ← Scanning MyApp.apk       [✕] │ ← Header with cancel
├─────────────────────────────────┤
│                                 │
│         🔍 Analyzing APK        │ ← Icon + Title
│                                 │
│ ┌─────────────────────────────┐ │
│ │████████████░░░░░░░  75%     │ │ ← Progress Bar
│ └─────────────────────────────┘ │
│                                 │
│ Extracting features...          │ ← Current Step
│ Estimated time: 15 seconds      │ ← ETA
│                                 │
│ Process Steps:                  │ ← Step Indicator
│ ✅ File validation              │
│ 🔄 Feature extraction          │
│ ⏳ ML classification           │
│                                 │
│         [Cancel Scan]           │ ← Cancel Button
│                                 │
├─────────────────────────────────┤
│ Processing... Please wait       │ ← Status Bar
└─────────────────────────────────┘
```

### 3. Results Screen Layout

```
┌─────────────────────────────────┐
│ ← MyApp.apk Results    [💾][📤] │ ← Header with actions
├─────────────────────────────────┤
│                                 │
│ ┌─────────────────────────────┐ │
│ │ 🚨 MALICIOUS DETECTED       │ │ ← Status Card (RED)
│ │                             │ │
│ │ Confidence: 94%             │ │
│ │ Risk Level: HIGH            │ │
│ │ Scanned: Oct 10, 2:30 PM    │ │
│ └─────────────────────────────┘ │
│                                 │
│ Top Threats ─────────────────   │ ← Threat Summary
│ ⚠️ Suspicious API calls         │   (Expandable)
│ 🔓 Excessive permissions        │
│ 🌐 Network anomalies           │
│                                 │
│ ═══ Analysis Details ═══        │ ← Section Divider
│                                 │
│ [Features] [Permissions] [ML]   │ ← Tab Navigation
│                                 │
│ Feature Analysis ─────────────  │ ← Current Tab Content
│ API Calls      ████████ 87%    │   (Chart/Graph)
│ Permissions    ██████   75%    │
│ Network        ████     68%    │
│                                 │
│ [Detailed Report] [Compare]     │ ← Action Buttons
│                                 │
├─────────────────────────────────┤
│ [🏠] [🔄] [📊] [ℹ️]           │ ← Bottom Navigation
└─────────────────────────────────┘
```

---

## 🎨 Visual State Variations

### Result Status Cards

#### ✅ SAFE (Green Theme)
```
┌─────────────────────────────────┐
│ ✅ SAFE & SECURE                │ GREEN
│                                 │ Background
│ Confidence: 98%                 │
│ No threats detected             │
└─────────────────────────────────┘
```

#### ⚠️ SUSPICIOUS (Orange Theme)  
```
┌─────────────────────────────────┐
│ ⚠️ POTENTIALLY RISKY            │ ORANGE
│                                 │ Background  
│ Confidence: 76%                 │
│ Manual review recommended       │
└─────────────────────────────────┘
```

#### 🚨 MALICIOUS (Red Theme)
```
┌─────────────────────────────────┐
│ 🚨 MALICIOUS DETECTED           │ RED
│                                 │ Background
│ Confidence: 94%                 │
│ Do not install this app         │
└─────────────────────────────────┘
```

---

## 🔗 Interactive Elements

### 1. Upload Zone States

```
DEFAULT STATE:
┌─────────────────────┐
│   📱 Drop APK Here  │ ← Dotted border
│                     │   Gray background
│   Tap to browse     │
└─────────────────────┘

HOVER/DRAG STATE:
┌─────────────────────┐
│ ⬇️  Drop to Upload   │ ← Solid blue border
│                     │   Light blue background  
│   Release to scan   │   Animated pulse
└─────────────────────┘

SUCCESS STATE:
┌─────────────────────┐
│ ✅ MyApp.apk Ready  │ ← Green border
│                     │   Light green background
│   [Start Scan]     │
└─────────────────────┘
```

### 2. Tab Navigation

```
INACTIVE TABS:          ACTIVE TAB:
┌─────────┐ ┌─────────┐ ┌─────────┐
│Features │ │Permissions│ │ML Data │
└─────────┘ └─────────┘ └─────────┘
                         ■■■■■■■■■ ← Active indicator
```

### 3. Progress Animations

```
SCAN PROGRESS:
Frame 1: 🔍      ○ ○ ○
Frame 2: ○ 🔍    ○ ○  
Frame 3: ○ ○ 🔍  ○
Frame 4: ○ ○ ○ 🔍

LOADING DOTS:
Frame 1: ●○○
Frame 2: ○●○
Frame 3: ○○●
```

---

## 📏 Responsive Breakpoints

### Phone Portrait (< 600dp)
```
┌─────────────────┐
│     Header      │ 60dp
├─────────────────┤
│                 │
│   Single Col    │ Flexible
│    Content      │
│                 │
├─────────────────┤
│  Bottom Nav     │ 56dp
└─────────────────┘
```

### Tablet/Landscape (> 600dp)
```
┌─────────────────────────────────┐
│           Header                │ 60dp
├─────────────────────────────────┤
│         │                       │
│  Side   │    Main Content       │ Flexible
│  Nav    │                       │
│  200dp  │                       │
├─────────────────────────────────┤
│          Status Bar             │ 40dp
└─────────────────────────────────┘
```

---

## 🎯 Touch Targets & Spacing

### Minimum Touch Targets
```
Buttons: 48dp × 48dp minimum
Icons: 24dp × 24dp (within 48dp touch area)
Text Fields: 48dp height minimum
List Items: 56dp height minimum
```

### Spacing System (8dp grid)
```
Micro: 4dp   (0.5 × base)
Small: 8dp   (1 × base)  
Medium: 16dp (2 × base)
Large: 24dp  (3 × base)
XLarge: 32dp (4 × base)
```

---

## 🔄 Animation Timing

```
Micro-interactions: 100-200ms
Screen transitions: 250-300ms
Loading animations: 1000ms loops
Progress updates: Immediate
```

---

*These wireframes provide the technical foundation for implementing the UI/UX redesign with precise measurements and interaction specifications.*