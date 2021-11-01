/*
 * License: MIT
 * Date created: 23 Jan 2019
 * @author navin
 */
package linux;

import irest.LockScreenDetector;
import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.util.logging.Level;
import java.util.logging.Logger;

public class LinuxScreenLockDetect extends LockScreenDetector {
    private final String command = "gdbus call -e -d com.canonical.Unity -o /com/canonical/Unity/Session -m com.canonical.Unity.Session.IsLocked";
    @Override
    public boolean isScreenLocked() {
        boolean locked = false;
        StringBuilder output = new StringBuilder();
        Process p;
        try {
            p = Runtime.getRuntime().exec(command);
            p.waitFor();
            BufferedReader reader = new BufferedReader(new InputStreamReader(p.getInputStream()));
            String result = reader.readLine();
            if (result != null) {
                if (result.contains("true")) {locked = true;}
            }
        } catch (IOException | InterruptedException ex) {Logger.getLogger(LinuxScreenLockDetect.class.getName()).log(Level.SEVERE, null, ex);}
        return locked;
    }
}
