/*
 * License: MIT
 * Date created: 23 Jan 2019
 * @author navin
 */
package sounds;

import java.applet.Applet;
import java.applet.AudioClip;
import java.util.logging.Level;
import java.util.logging.Logger;

public class PlaySound {

    public void PlayBeep() {   
        try {
            AudioClip clip = Applet.newAudioClip(getClass().getResource("/sounds/beep3.wav"));
            clip.play();
        } catch(Exception ex) {{Logger.getLogger(PlaySound.class.getName()).log(Level.WARNING, null, ex);}}
    }
}
