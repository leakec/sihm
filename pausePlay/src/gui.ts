import { GUI, GUIController } from "dat.gui";
import * as THREE from "three";

export class MyGui extends GUI {
  video_controls: GUI;
  pause_play_button: GUIController;
  loop_button: GUIController;
  time_slider: GUIController;
  clip_action: THREE.AnimationAction;
  looping: boolean;
  max_time: number;

  add_video_controls(
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

  pause() {
    // Called when the animation is paused
    this.pause_play_button.name("\u25B6");
  }

  play() {
    // Called when the animation is played
    this.pause_play_button.name("\u23F8");
  }

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

  update_time() {
    this.updateControllerWithoutCB(this.time_slider, this.clip_action.time);
  }

  updateControllerWithoutCB(cont: GUIController, value: any) {
    // Updates controller value without triggering the CB
    cont.object[cont.property] = value;
    cont.updateDisplay();
  }
}
