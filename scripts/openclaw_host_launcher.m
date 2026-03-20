#import <Foundation/Foundation.h>
#import <signal.h>

#ifndef OPENCLAW_PROJECT_DIR
#define OPENCLAW_PROJECT_DIR ""
#endif

#ifndef OPENCLAW_TARGET_SCRIPT
#define OPENCLAW_TARGET_SCRIPT ""
#endif

#ifndef OPENCLAW_HOST_BUNDLE_ID
#define OPENCLAW_HOST_BUNDLE_ID ""
#endif

#ifndef OPENCLAW_HOST_APP_PATH
#define OPENCLAW_HOST_APP_PATH ""
#endif

static NSTask *gTask = nil;

static void forward_signal(int signo) {
  if (gTask != nil && gTask.isRunning) {
    kill(gTask.processIdentifier, signo);
  }
}

int main(int argc, const char * argv[]) {
  @autoreleasepool {
    signal(SIGTERM, forward_signal);
    signal(SIGINT, forward_signal);
    signal(SIGHUP, forward_signal);

    NSString *projectDir = @OPENCLAW_PROJECT_DIR;
    NSString *targetScript = @OPENCLAW_TARGET_SCRIPT;
    NSString *hostBundleId = @OPENCLAW_HOST_BUNDLE_ID;
    NSString *hostAppPath = @OPENCLAW_HOST_APP_PATH;

    if (projectDir.length == 0 || targetScript.length == 0) {
      fprintf(stderr, "Missing embedded launcher configuration.\n");
      return 64;
    }

    NSMutableDictionary<NSString *, NSString *> *env =
        [NSMutableDictionary dictionaryWithDictionary:[[NSProcessInfo processInfo] environment]];
    env[@"OPENCLAW_HOST_BUNDLE_ID"] = hostBundleId;
    env[@"OPENCLAW_HOST_APP_PATH"] = hostAppPath;

    NSTask *task = [[NSTask alloc] init];
    gTask = task;
    task.executableURL = [NSURL fileURLWithPath:@"/bin/bash"];
    task.arguments = @[targetScript];
    task.currentDirectoryURL = [NSURL fileURLWithPath:projectDir isDirectory:YES];
    task.environment = env;
    task.standardInput = [NSFileHandle fileHandleWithStandardInput];
    task.standardOutput = [NSFileHandle fileHandleWithStandardOutput];
    task.standardError = [NSFileHandle fileHandleWithStandardError];

    NSError *error = nil;
    if (![task launchAndReturnError:&error]) {
      fprintf(stderr, "Failed to launch child script: %s\n", error.localizedDescription.UTF8String);
      return 70;
    }

    [task waitUntilExit];
    int status = task.terminationStatus;
    gTask = nil;
    return status;
  }
}
