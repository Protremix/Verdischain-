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
    
    let result = super.application(application, didFinishLaunchingWithOptions: launchOptions)
    
    NSLog("VERDIS_DEBUG: super.application returned \(result)")
    
    // NATIVE DEBUG: Set window background to RED so we can verify
    // native iOS rendering works even if Flutter fails to render
    DispatchQueue.main.async {
      if let window = self.window {
        window.backgroundColor = UIColor.red
        NSLog("VERDIS_DEBUG: Window background set to RED")
        
        // Add a native label on top of everything
        let label = UILabel(frame: CGRect(x: 20, y: 100, width: 350, height: 60))
        label.text = "NATIVE iOS WORKS"
        label.textColor = UIColor.white
        label.backgroundColor = UIColor.black
        label.textAlignment = .center
        label.font = UIFont.boldSystemFont(ofSize: 20)
        label.layer.cornerRadius = 8
        label.clipsToBounds = true
        window.addSubview(label)
        window.bringSubviewToFront(label)
        NSLog("VERDIS_DEBUG: Native label added to window")
      } else {
        NSLog("VERDIS_DEBUG: Window is nil!")
      }
    }
    
    return result
  }
}
