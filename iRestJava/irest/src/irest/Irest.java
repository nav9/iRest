/*
 * License: MIT
 * Date created: 23 Jan 2019
 * @author navin
 */
package irest;

//String phone = "012-3456789";
//	String[] output = phone.split("-");
//	System.out.println(output[0]);
//	System.out.println(output[1]);

public class Irest {
    public static void main(String[] args) {
        DataManager dat = new DataManager();
        dat.createStatesAndStart();
        //---main loop that runs while the system runs
        while(true) {
            dat.currentState.run();
        }            
    }    
}
