import UIKit
import Flutter

class SceneDelegate: UIResponder, UIWindowSceneDelegate {
    var window: UIWindow?

    func scene(_ scene: UIScene, willConnectTo session: UISceneSession, options connectionOptions: UIScene.ConnectionOptions) {
        guard let windowScene = scene as? UIWindowScene else { return }

        // Use the Main.storyboard's FlutterViewController
        let storyboard = UIStoryboard(name: "Main", bundle: nil)
        let flutterVC = storyboard.instantiateInitialViewController()!

        let window = UIWindow(windowScene: windowScene)
        window.rootViewController = flutterVC
        window.makeKeyAndVisible()
        self.window = window

        // Connect to AppDelegate so Flutter plugins work
        if let appDelegate = UIApplication.shared.delegate as? AppDelegate {
            appDelegate.window = window
        }

        NSLog("VERDIS_DEBUG: SceneDelegate created window with FlutterViewController")
    }
}
