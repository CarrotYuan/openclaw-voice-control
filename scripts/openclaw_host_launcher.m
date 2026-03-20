#import <Foundation/Foundation.h>
#include <stdlib.h>
#include <unistd.h>

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

int main(int argc, const char * argv[]) {
  @autoreleasepool {
    NSString *projectDir = @OPENCLAW_PROJECT_DIR;
    NSString *targetScript = @OPENCLAW_TARGET_SCRIPT;
    NSString *hostBundleId = @OPENCLAW_HOST_BUNDLE_ID;
    NSString *hostAppPath = @OPENCLAW_HOST_APP_PATH;

    if (projectDir.length == 0 || targetScript.length == 0) {
      fprintf(stderr, "Missing embedded launcher configuration.\n");
      return 64;
    }

    if (setenv("OPENCLAW_HOST_BUNDLE_ID", hostBundleId.UTF8String, 1) != 0 ||
        setenv("OPENCLAW_HOST_APP_PATH", hostAppPath.UTF8String, 1) != 0) {
      fprintf(stderr, "Failed to set launcher environment.\n");
      return 70;
    }

    if (chdir(projectDir.fileSystemRepresentation) != 0) {
      perror("Failed to change directory");
      return 72;
    }

    execl(targetScript.fileSystemRepresentation, targetScript.fileSystemRepresentation, (char *)NULL);
    perror("Failed to exec target script");
    return 71;
  }
}
