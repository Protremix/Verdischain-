import Flutter
import UIKit

@main
@objc class AppDelegate: UIResponder, UIApplicationDelegate {
  var window: UIWindow?

  override func application(
    _ application: UIApplication,
    didFinishLaunchingWithOptions launchOptions: [UIApplication.LaunchOptionsKey: Any]?
  ) -> Bool {
    // iOS loads Main.storyboard automatically (UIMainStoryboardFile in Info.plist)
    // Main.storyboard has FlutterViewController as initialViewController
    // FlutterViewController creates its own FlutterEngine and renders Dart code
    // We do NOT create a window here — iOS does it from the storyboard

    NSLog("VERDIS_DEBUG: AppDelegate started — storyboard will create window")

    return true
  }
}
