import { GUI, GUIController } from "dat.gui";
import { MyCamera } from "./camera";
import * as THREE from "three";

export class MyGui extends GUI {
    /** This is the folder of video controls. */
    video_controls: GUI;

    /** This is the GUI button to pause/play. */
    pause_play_button: GUIController;

    /** This is the GUI button to loop once vs. loop infinitely. */
    loop_button: GUIController;

    /** This is the GUI slider that can be used to change the video time. */
    time_slider: GUIController;

    /** This is the clip action that is being controlled by the video controls. */
    clip_action: THREE.AnimationAction;

    /** Indicates wether the video is looping or not. */
    looping: boolean;

    /** Duration of the action clip. */
    max_time: number;

    /** This is the folder of camera controls. */
    camera_controls: GUI;

    /** The camera that is being controlled by the camera controls. */
    camera: MyCamera;

    /** Controls which object the camera is following. */
    follow_control: GUIController;

    /** This method adds the video controls.
     * @param pause_play_func {() => void} A function used to pause/play the animation clip.
     * @param set_time_func {() => void} A function used to set the time of the anmiation clip.
     * @param clip_action {THREE.AnimationAction} The clip action that the video controls will control.
     */
    addVideoControls(
        pause_play_func: () => void,
        set_time_func: () => void,
        clip_action: THREE.AnimationAction,
    ) {
        this.video_controls = this.addFolder("Video controls");

        this.clip_action = clip_action;

        // Add pause/play
        this.pause_play_button = this.video_controls.add(
            { "Pause/Play": pause_play_func },
            "Pause/Play",
        );
        this.pause_play_button.name("\u23F8");

        // Add looping controls
        var func = this.set_loop.bind(this); // Binding this to its method so we can pass it as a standalone function
        this.loop_button = this.video_controls.add({ loop: func }, "loop");
        this.loop_button.name("\uD83D\uDD03");
        this.looping = true;

        // Add slider for time
        this.max_time = this.clip_action.getClip().duration;
        this.time_slider = this.video_controls.add(
            { Time: 0.0 },
            "Time",
            0.0,
            this.max_time,
        );
        this.time_slider.onChange(set_time_func);
        this.video_controls.open();
    }

    addCameraControls(camera: MyCamera) {
        this.camera = camera;

        this.camera_controls = this.addFolder("Camera controls");
        var follow_obj = {};
        follow_obj["None"] = -1;
        this.camera.followable_objs.forEach(
            (obj) => (follow_obj[obj.name] = obj.id),
        );
        this.follow_control = this.camera_controls.add(
            { name: "Follow object" },
            "name",
            follow_obj,
        );
        var func = this.setCameraToFollow.bind(this); // Binding this to its method so we can pass it as a standalone function
        this.follow_control.onChange(func);
        this.follow_control.setValue(-1);
    }

    /**
     * Sets the camera to follow the given object.
     * @param id {number} The id of the object to follow.
     */
    setCameraToFollow(id: number) {
        if (id < 0) {
            this.camera.follow_obj = null;
        } else {
            // Need to call Math.trunc on this, otherwise a float gets passed in which leads to an undefined
            // object.
            this.camera.follow_obj = this.camera.scene.getObjectById(
                Math.trunc(id),
            );
        }
    }

    /**
     * This is called when the animation is paused.
     */
    pause() {
        // Change the button symbol to use the "pause" unicode character
        this.pause_play_button.name("\u25B6");
    }

    /**
     * This is called when the animation is played.
     */
    play() {
        // Change the button symbol to use the "play" unicode character
        this.pause_play_button.name("\u23F8");
    }

    /**
     * This function changes the loop status (single vs. infinite).
     */
    set_loop() {
        if (this.looping) {
            // Called when loop is disabled
            this.looping = false;
            this.clip_action.setLoop(THREE.LoopOnce, Infinity);

            // Change looping icon and mode
            // Using surrogate pairs to render 5 digit unicode character.
            // See: http://www.russellcottrell.com/greek/utilities/SurrogatePairCalculator.htm
            this.loop_button.name("\uD83D\uDD02");
        } else {
            // Called when loop is enabled
            this.looping = true;
            this.clip_action.setLoop(THREE.LoopRepeat, Infinity);
            this.clip_action.reset().play();

            // Change looping icon and mode
            // Using surrogate pairs to render 5 digit unicode character.
            // See: http://www.russellcottrell.com/greek/utilities/SurrogatePairCalculator.htm
            this.loop_button.name("\uD83D\uDD03");
        }
    }

    /**
     * This method updates the time slider with the video animations current time.
     */
    update_time() {
        this.updateControllerWithoutCB(this.time_slider, this.clip_action.time);
    }

    /**
     * This method updates a controllers value without triggering its onChange function.
     * @param cont {GUIController} The controller whose value is being changed.
     * @param value {any} The value to change the controller to.
     */
    updateControllerWithoutCB(cont: GUIController, value: any) {
        cont.object[cont.property] = value;
        cont.updateDisplay();
    }
}
