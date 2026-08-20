import Flutter
import UIKit

@main
@objc class AppDelegate: FlutterAppDelegate {
  override func application(
    _ application: UIApplication,
    didFinishLaunchingWithOptions launchOptions: [UIApplication.LaunchOptionsKey: Any]?
  ) -> Bool {
    NSLog("VERDIS_DEBUG: AppDelegate started")

    GeneratedPluginRegistrant.register(with: self)

    // With UIApplicationSceneManifest in Info.plist, iOS 13+ uses SceneDelegate
    // to create the window. We still call super for Flutter engine setup.
    let result = super.application(application, didFinishLaunchingWithOptions: launchOptions)

    NSLog("VERDIS_DEBUG: super.application returned \(result)")
    return result
  }
}
