import 'dart:async';
import 'package:flutter/widgets.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../config/network_config.dart';

/// Session manager that auto-locks the wallet after a period of inactivity.
/// Enforces: 2-minute session timeout, 1-minute auto-lock when backgrounded.
final sessionManagerProvider = StateNotifierProvider<SessionManager, SessionState>((ref) {
  return SessionManager();
});

enum SessionState {
  active,
  locked,
  background,
}

class SessionManager extends StateNotifier<SessionState> {
  SessionManager() : super(SessionState.active);

  Timer? _sessionTimer;
  Timer? _backgroundTimer;
  DateTime? _lastActivity;
  static const int _sessionTimeoutSeconds = 120; // 2 minutes
  static const int _autoLockSeconds = 60; // 1 minute when backgrounded

  void registerActivity() {
    _lastActivity = DateTime.now();
    _sessionTimer?.cancel();
    _sessionTimer = Timer(
      const Duration(seconds: _sessionTimeoutSeconds),
      () => lock(),
    );
    if (state == SessionState.locked) {
      state = SessionState.active;
    }
  }

  void onAppPaused() {
    _sessionTimer?.cancel();
    _backgroundTimer?.cancel();
    _backgroundTimer = Timer(
      const Duration(seconds: _autoLockSeconds),
      () => lock(),
    );
    state = SessionState.background;
  }

  void onAppResumed() {
    _backgroundTimer?.cancel();
    // If we were backgrounded long enough to trigger lock, stay locked
    if (state == SessionState.locked) return;
    // Check if session expired while backgrounded
    if (_lastActivity != null) {
      final elapsed = DateTime.now().difference(_lastActivity!).inSeconds;
      if (elapsed >= _sessionTimeoutSeconds) {
        lock();
        return;
      }
    }
    state = SessionState.active;
    registerActivity();
  }

  void lock() {
    _sessionTimer?.cancel();
    _backgroundTimer?.cancel();
    state = SessionState.locked;
  }

  void unlock() {
    state = SessionState.active;
    registerActivity();
  }

  void dispose() {
    _sessionTimer?.cancel();
    _backgroundTimer?.cancel();
  }
}

/// Widget that monitors app lifecycle and feeds events to SessionManager
class SessionLifecycleObserver extends ConsumerStatefulWidget {
  const SessionLifecycleObserver({required this.child, super.key});
  final Widget child;

  @override
  ConsumerState<SessionLifecycleObserver> createState() => _SessionLifecycleObserverState();
}

class _SessionLifecycleObserverState extends ConsumerState<SessionLifecycleObserver>
    with WidgetsBindingObserver {
  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addObserver(this);
  }

  @override
  void dispose() {
    WidgetsBinding.instance.removeObserver(this);
    super.dispose();
  }

  @override
  void didChangeAppLifecycleState(AppLifecycleState lifecycleState) {
    final session = ref.read(sessionManagerProvider.notifier);
    switch (lifecycleState) {
      case AppLifecycleState.paused:
      case AppLifecycleState.inactive:
        session.onAppPaused();
        break;
      case AppLifecycleState.resumed:
        session.onAppResumed();
        break;
      case AppLifecycleState.detached:
        session.lock();
        break;
      case AppLifecycleState.hidden:
        break;
    }
  }

  @override
  Widget build(BuildContext context) {
    // Register activity on every build (user interaction)
    ref.read(sessionManagerProvider.notifier).registerActivity();
    return widget.child;
  }
}
