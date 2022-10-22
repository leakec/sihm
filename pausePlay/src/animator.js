import * as THREE from 'three';

export class MyMixer extends THREE.AnimationMixer
{
	key_frame_tracks = [];
	max_time = 0.0;

	addKeyFrameTrack(key_frame_track)
	{
		// Add key frame track to mixer
		this.key_frame_tracks.push(key_frame_track);
		var time = Math.max(key_frame_track.times);
		if (time > this.max_time)
		{
			this.max_time = time;
		}
	}

	lock()
	{
		// Used to lock the mixer. This creates the clip 
		this.clip = new THREE.AnimationClip( 'Action', -1, this.key_frame_tracks);
		this.clip.resetDuration();
		this.clipAction = this.clipAction( this.clip );
		this.clipAction.play();
	}
}
