import * as THREE from 'three';

export class MyMixer extends THREE.AnimationMixer
{
	keyframe_tracks = [];
	max_time = 0.0;

	addKeyframeTrack(keyframe_track)
	{
		// Add key frame track to mixer
		this.keyframe_tracks.push(keyframe_track);
		var time = Math.max(keyframe_track.times);
		if (time > this.max_time)
		{
			this.max_time = time;
		}
	}

	lock()
	{
		// Used to lock the mixer. This creates the clip 
		this.clip = new THREE.AnimationClip( 'Action', -1, this.keyframe_tracks);
		this.clip.resetDuration();
		this.clipAction = this.clipAction( this.clip );
		this.clipAction.play();
	}
}
