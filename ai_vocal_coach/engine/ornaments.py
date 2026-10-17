"""Grace-note attacks from energy entrances and confident pitch changes."""
import numpy as np
from scipy.signal import find_peaks
from utils.exercise_models import note_grid


def attacks(f):
    from engine.exercise_analysis import detect_attacks,cents
    energy=detect_attacks(f,.06)
    log=cents(f.f0,440);change=np.zeros(len(log))
    for i in range(3,len(log)-3):
        if np.all(f.voiced[i-3:i+3]):
            change[i]=abs(np.median(log[i:i+3])-np.median(log[i-3:i]))
    peaks,_=find_peaks(change,height=65,distance=6)
    # Distinct pitch changes can be legato attacks with no energy dip.
    # Prefer those over an energy peak displaced by tracker-window latency.
    candidates=list(peaks)
    for i in energy:
        if not any(abs(i-j)<=6 for j in candidates):candidates.append(int(i))
    return np.asarray(sorted(candidates),dtype=int)


def ornament_rules(f,p,ctx,r,root):
    from engine.exercise_analysis import cents,accuracy
    bounds,offsets=note_grid(p,ctx.get('bpm'));t=f.relative_times
    shared=ctx.get('performance_start_seconds')
    origin=float(shared)-f.origin if shared is not None else 0
    onset_indices=attacks(f);onsets=t[onset_indices]
    main=root
    if not main:
        v=f.f0[f.voiced&(t>.2)&(t<.7)]
        main=float(np.median(v)) if len(v)>4 else None
    clarity=[];errors=[];timing=[];directions=set();observed_main=[];used=set()
    for k in range(4):
        a,b,c=bounds[2*k:2*k+3]+origin
        # Find an actual main-note attack, not just an expected sample window.
        candidates=[]
        for j,at in zip(onset_indices,onsets):
            if j in used or not b-.1<=at<min(c-.1,b+.4):continue
            after=f.f0[j+2:min(len(t),j+15)];after=after[np.isfinite(after)]
            if len(after)>=4 and main and abs(float(cents(np.median(after),main)))<70:candidates.append((abs(at-b),j,at))
        chosen=min(candidates) if candidates else None
        main_at=chosen[2] if chosen else None
        if chosen:used.add(chosen[1]);observed_main.append(main_at)
        grace_candidates=[]
        if chosen:
            for j,at in zip(onset_indices,onsets):
                if a-.2<=at<main_at-.04:
                    region=f.f0[j+1:max(j+2,min(len(t),int((main_at+f.origin)/.01)-1))];region=region[np.isfinite(region)]
                    if len(region)>=3 and abs(float(cents(np.median(region),main))-offsets[2*k]*100)<80:grace_candidates.append((at,float(np.median(region))))
        if grace_candidates:
            grace_at,grace_pitch=grace_candidates[-1];duration=main_at-grace_at
            clarity.append(1 if duration<=.25 else .3);directions.add(1 if grace_pitch>main else -1)
            if duration>.25:r.event('long_grace','The grace note is taking too much time — make it quicker and lighter.',grace_at,'Grace Note Clarity')
        else:
            # Untrackable audio is unknown, whereas a confident unornamented
            # main note is evidence that the grace note was skipped.
            region=(t>=a)&(t<max(a+.04,main_at or b))
            if np.sum(f.voiced&region)>=3:
                clarity.append(0);r.event('missing_grace','The grace note did not come through — add a distinct quick pitch before the main note.',a,'Grace Note Clarity')
            else:r.event('grace_tracking','This grace-note window was not tracked clearly and was excluded. Try again a little slower or clearer.',a,valence='neutral')
        if chosen:
            error=main_at-b;timing.append(abs(error))
            if error>.06:r.event('late_main','The grace note is delaying the main beat — borrow time before the beat.',main_at,'Beat Stability')
            held=(t>=main_at+.04)&(t<min(c-.03,main_at+.5))&f.voiced
            pitch=f.f0[held]
            if len(pitch)>=4:errors.append(abs(float(cents(np.median(pitch),main))))
            settle=np.flatnonzero((t>=main_at)&(t<min(c,main_at+.35))&f.voiced&(np.abs(cents(f.f0,main))<30))
            if len(settle) and t[settle[0]]-main_at>.15:r.event('landing_slide','Let the main pitch arrive directly instead of sliding into it.',main_at,'Landing Accuracy')
    if clarity:r.metric('Grace Note Clarity',100*np.mean(clarity),'Distinct grace and main attacks checked using confident pitch transitions and energy entrances.',distinct_pairs=float(sum(clarity)),assessed_pairs=len(clarity),detected_attacks=onsets.tolist())
    else:r.unavailable('Grace Note Clarity','Grace-note tracking was insufficient; no clarity score is guessed.')
    if timing:r.metric('Beat Stability',100-500*np.mean(timing),'Main-note attacks compared with '+('the recorder count-in clock.' if shared is not None else 'a relative beat grid; use live cues for absolute entrance timing.'),mean_attack_error_seconds=float(np.mean(timing)),synchronized=shared is not None,main_attacks=observed_main)
    else:r.unavailable('Beat Stability','Two distinct attacks per pair could not be resolved. Record a clear grace note before each sustained main note.')
    if errors:r.metric('Landing Accuracy',accuracy(np.mean(errors)),'Held main-note pitch compared with the first confirmed main note.',mean_absolute_cents=float(np.mean(errors)))
    else:r.unavailable('Landing Accuracy','Main-note plateaus were not clear enough to score.')
    if len(directions)<2:r.event('ornament_direction','Try the grace note from above twice, then from below twice.',metric='Grace Note Clarity')
