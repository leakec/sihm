import * as THREE from "three";

export class MyMixer extends THREE.AnimationMixer {
  keyframe_tracks: THREE.KeyframeTrack[] = [];
  clip: THREE.AnimationClip;
  clip_action: THREE.AnimationAction;

  addKeyframeTrack(keyframe_track: THREE.KeyframeTrack) {
    // Add key frame track to mixer
    this.keyframe_tracks.push(keyframe_track);
  }

  lock() {
    // Used to lock the mixer. This creates the clip
    this.clip = new THREE.AnimationClip("Action", -1, this.keyframe_tracks);
    this.clip.resetDuration();
    this.clip_action = this.clipAction(this.clip);
    this.clip_action.play();
  }
}
