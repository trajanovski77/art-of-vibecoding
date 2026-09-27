// Lists on-screen windows of the Claude desktop app: "<windowID>\t<width>x<height>\t<title>"
import CoreGraphics
import Foundation
let owner = CommandLine.arguments.count > 1 ? CommandLine.arguments[1] : "Claude"
let opts = CGWindowListOption(arrayLiteral: .optionOnScreenOnly, .excludeDesktopElements)
guard let info = CGWindowListCopyWindowInfo(opts, kCGNullWindowID) as? [[String: Any]] else { exit(1) }
for w in info {
    guard let o = w[kCGWindowOwnerName as String] as? String, o == owner,
          let layer = w[kCGWindowLayer as String] as? Int, layer == 0,
          let id = w[kCGWindowNumber as String] as? Int,
          let b = w[kCGWindowBounds as String] as? [String: Any],
          let wd = b["Width"] as? Double, let ht = b["Height"] as? Double, wd > 400 else { continue }
    let title = (w[kCGWindowName as String] as? String) ?? ""
    print("\(id)\t\(Int(wd))x\(Int(ht))\t\(title)")
}
