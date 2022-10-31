import { GUI } from "dat.gui";
import * as THREE from "three";
export class MyGui extends GUI {
    constructor() {
        super(...arguments);
        /** Enables/disables rotating with object. */
        this.rotate_with_object = true;
    }
    /** This method adds the video controls.
     * @param pause_play_func {() => void} A function used to pause/play the animation clip.
     * @param mixer {MyMixer} The mixer that owns the animation clip.
     */
    addVideoControls(pause_play_func, mixer) {
        this.mixer = mixer;
        this.clip_action = mixer.clip_action;
        this.video_controls = this.addFolder("Video controls");
        // Add pause/play
        this.pause_play_button = this.video_controls.add(
            { "Pause/Play": pause_play_func },
            "Pause/Play",
        );
        this.pause_play_button.name("\u23F8");
        // Add looping controls
        var func = this.setLoop.bind(this); // Binding this to its method so we can pass it as a standalone function
        this.loop_button = this.video_controls.add({ loop: func }, "loop");
        this.loop_button.name("\uD83D\uDD03");
        this.looping = true;
        // Add a slider for real-time factor
        this.real_time_slider = this.video_controls.add(
            { rt: 1.0 },
            "rt",
            0.01,
            5.0,
        );
        var func2 = this.updateRealTimeFactor.bind(this); // Binding this to its method so we can pass it as a standalone function
        this.real_time_slider.onChange(func2);
        this.real_time_slider.name("Real time factor");
        this.real_time_slider.setValue(1.0);
        // Add slider for time
        this.max_time = this.clip_action.getClip().duration;
        this.time_slider = this.video_controls.add(
            { Time: 0.0 },
            "Time",
            0.0,
            this.max_time,
        );
        this.time_slider.onChange(this.setTime.bind(this));
        this.video_controls.open();
    }
    /**
     * Adds the camera controls.
     * @param camera { MyCamera } - the camera to add the camera controls to.
     */
    addCameraControls(camera) {
        this.camera = camera;
        // Create folder
        this.camera_controls = this.addFolder("Camera controls");
        // Setup drop down list to choose which object to follow
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
        this.follow_control.name("Follow object");
        this.follow_control.onChange(func);
        this.follow_control.setValue(-1);
        // Setup checkbox to enable/disable rotate with object
        this.rotation_control = this.camera_controls.add(
            { value: true },
            "value",
        );
        this.rotation_control.name("Rotate with object");
        this.rotation_control.setValue(true);
        var func2 = this.setCameraRotation.bind(this); // Binding this to its method so we can pass it as a standalone function
        this.rotation_control.onChange(func2);
    }
    /**
     * This callback enables/disables rotating a camera with the object it is following.
     * @param val {boolean} This boolean determines whether rotation is enabled (true) or disabled (false).
     */
    setCameraRotation(val) {
        this.rotate_with_object = val;
        this.camera.rotation = val;
        this.setCameraToFollow(this.follow_control.getValue());
    }
    /**
     * Sets the camera to follow the given object.
     * @param id {number} The id of the object to follow.
     */
    setCameraToFollow(id) {
        if (id < 0) {
            this.camera.follow_obj = null;
            this.camera.scene.add(this.camera.camera);
        } else {
            // Need to call Math.trunc on this, otherwise a float gets passed in which leads to an undefined
            // object.
            this.camera.follow_obj = this.camera.scene.getObjectById(
                Math.trunc(id),
            );
            if (this.rotate_with_object) {
                this.camera.follow_obj.attach(this.camera.camera);
            } else {
                this.camera.scene.attach(this.camera.camera);
                var wpc = new THREE.Vector3();
                var wpo = new THREE.Vector3();
                this.camera.camera.getWorldPosition(wpc);
                this.camera.follow_obj.getWorldPosition(wpo);
                this.camera.follow_obj_offset.subVectors(wpc, wpo);
            }
        }
    }
    /**
     * This method changes the real-time factor of the animation mixer.
     * @param real_time_factor {number} Real-time factor.
     */
    updateRealTimeFactor(real_time_factor) {
        this.clip_action.setEffectiveTimeScale(real_time_factor);
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
    setLoop() {
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
    updateTime() {
        this.updateControllerWithoutCB(this.time_slider, this.clip_action.time);
    }
    /**
     * Set the mixer's time.
     * @param value{number} Time to set the mixer to.
     */
    setTime(value) {
        this.mixer.setTime(value / this.clip_action.getEffectiveTimeScale());
    }
    /**
     * This method updates a controllers value without triggering its onChange function.
     * @param cont {GUIController} The controller whose value is being changed.
     * @param value {any} The value to change the controller to.
     */
    updateControllerWithoutCB(cont, value) {
        cont.object[cont.property] = value;
        cont.updateDisplay();
    }
}
