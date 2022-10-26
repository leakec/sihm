import * as THREE from "three";

export class MyMixer extends THREE.AnimationMixer {
    /** An array of keyframe tracks that make up the animation clip. */
    keyframe_tracks: THREE.KeyframeTrack[] = [];

    /** This is the animation clip, which is composed of the keyframe tracks. */
    clip: THREE.AnimationClip;

    /** This is the animation clip action for the animation clip. */
    clip_action: THREE.AnimationAction;

    /**
     * Adds keyframe track to the clip.
     * @param keyframe_track {THREE.KeyframeTrack} - Keyframe track to add to the clip.
     */
    addKeyframeTrack(keyframe_track: THREE.KeyframeTrack) {
        // Add key frame track to mixer
        this.keyframe_tracks.push(keyframe_track);
    }

    /** This method locks the object and makes it ready for use.
     *  This should be done before the anmiation is started.
     */
    lock() {
        // Used to lock the mixer. This creates the clip
        this.clip = new THREE.AnimationClip("Action", -1, this.keyframe_tracks);
        this.clip.resetDuration();
        this.clip_action = this.clipAction(this.clip);
        this.clip_action.play();
    }
}
