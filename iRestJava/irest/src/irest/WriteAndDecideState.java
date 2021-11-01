package irest;

public class WriteAndDecideState extends State {
    private DataManager dat = null;
    WriteAndDecideState(DataManager d) {
        dat = d;
    }
    
    @Override
    public void run() {
        dat.fileMgr.writeToFileByOverwriting();
        if (dat.isScreenLocked() == false && dat.userNeedsToBeRemindedToStop()) {
            dat.currentState = dat.reminderState;
        } else {
            dat.currentState = dat.bigSleepState;
        }
    }    
    
}
