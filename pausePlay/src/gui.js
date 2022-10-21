import { GUI } from 'dat.gui'

export class MyGui extends GUI
{
	add_video_controls(pause_play_func, set_time_func, max_time)
	{
		this.video_controls = this.addFolder('Video controls')
		this.pause_play_button = this.video_controls.add({"Pause/Play": pause_play_func}, "Pause/Play");
		this.pause_play_button.name("\u23F8")

		this.max_time = max_time
		this.time_slider = this.video_controls.add({"Time": 0.0}, "Time", 0.0, max_time);
		this.time_slider.onChange(set_time_func);
		this.video_controls.open()
	}

	pause()
	{
		// Called when the animation is paused
		this.pause_play_button.name("\u25B6");
	}

	play()
	{
		// Called when the animation is played
		this.pause_play_button.name("\u23F8");
	}

	update_time(delta)
	{
		var time = (this.time_slider.getValue() + delta) % this.max_time;
		this.updateControllerWithoutCB(this.time_slider, time);
	}

	updateControllerWithoutCB(cont, value)
	{
		// Updates controller value without triggering the CB
		cont.object[cont.property] = value;
		cont.updateDisplay();
	}
}
