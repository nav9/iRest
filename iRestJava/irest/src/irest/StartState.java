package irest;

public class StartState extends State {
    private DataManager dat = null;
    StartState(DataManager d) {
        dat = d;
    }
    @Override
    public void run() {
        dat.currentState = dat.bigSleepState;
    }    
    
}
