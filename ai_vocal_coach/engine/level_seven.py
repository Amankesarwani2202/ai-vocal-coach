"""Measured Level 7 checks. Acoustic proxies never diagnose anatomy."""
import numpy as np
from scipy.signal import find_peaks
from utils.exercise_models import note_grid


def evaluate(f, p, ctx, r, notes=None, root=None):
    from engine.exercise_analysis import cents, accuracy, internal_gaps, formant_track, runs
    t=f.relative_times
    code=p['code']
    def metric(name,value,text,**evidence): r.metric(name,value,text,**evidence)
    def event(rule,text,at=0,metric=None,**extra): r.event(rule,text,at,metric,**extra)
    def window(a,b): return f.voiced & (t>=a) & (t<b)
    def measured_pitch(a,b):
        v=f.f0[window(a,b)]
        return float(np.median(v)) if len(v)>=4 else None
    def rename(old,new):
        if old in r.scores:
            r.scores[new]=r.scores.pop(old);r.evidence[new]=r.evidence.pop(old)
        if old in r.withheld:r.withheld[new]=r.withheld.pop(old)
        for e in r.feedback:
            if e.get('metric')==old:e['metric']=new;e['message']=e['message'].replace(old,new)
    if code=='7.1':
        rename('Register Connection','Pitch Connection')
        base=ctx.get('root_hz') or measured_pitch(.08,.4)
        zone=ctx.get('passaggio_zone_hz')
        if base and zone and base<=zone[0]<zone[1]<=base*2**(7/12):
            r.event('known_zone_crossing','This interval crosses the transition zone you supplied. Let the tone lighten gently through it; anatomical register changes are not diagnosed from audio.',valence='neutral',timing='Summary')
        if base:
            arrivals=[(3.08,3.45,base*2**(7/12)),(6.08,6.45,base)]
            errors=[]
            for a,b,target in arrivals:
                hz=measured_pitch(a,b)
                if hz:
                    err=float(cents(hz,target));errors.append(abs(err))
                    if abs(err)>30:event('arrival','You landed '+('sharp' if err>0 else 'flat')+' of the target — let the glide settle exactly on it.',a,'Arrival Accuracy')
            if errors:metric('Arrival Accuracy',accuracy(np.mean(errors)),'Held arrivals compared with the fifth and returning tonic.',mean_absolute_cents=float(np.mean(errors)))
            else:r.unavailable('Arrival Accuracy','Record both held arrivals after the upward and downward glides.')
            opening=f.f0[window(.3,.7)]
            if len(opening) and np.nanmin(cents(opening,base)) < -40:event('start_scoop','There’s a dip before the glide starts — begin right from your held pitch.',.3,'Pitch Connection')
            high=np.flatnonzero(window(.5,3.5)&(cents(f.f0,base)>650))
            if len(high) and t[high[0]]-.5<1.75:event('rushed_glide','That glide moved faster than slow and even — stretch it out.',t[high[0]],'Glide Smoothness')
            end=measured_pitch(6.05,6.45)
            if not end:event('missing_return','Don’t forget to repeat the glide coming back down.',min(3.5,f.duration),'Arrival Accuracy')
    if code=='7.2':
        # Discrete target changes are intentional, not register breaks.
        rename('Continuity','Register Release')
        # Ignore the expected staircase changes and every untracked frame.
        bounds,_=note_grid(p,ctx.get('bpm'))
        log=cents(f.f0,440);pairs=f.voiced[1:]&f.voiced[:-1]
        jump=np.flatnonzero(pairs & (np.nan_to_num(np.abs(np.diff(log)))>180))
        jumps=[i for i in jump if np.min(np.abs(bounds-t[i]))>.15]
        old=r.scores.get('Register Release',100)
        if jumps:
            r.scores.pop('Register Release',None);r.evidence.pop('Register Release',None)
            r.feedback=[e for e in r.feedback if not (e.get('metric')=='Register Release' and e.get('timing')=='Summary')]
            metric('Register Release',old-18*len(jumps),'Connected sound and abrupt discontinuities within held notes; written pitch changes and tracking loss are excluded.',discontinuities=len(jumps))
            for i in jumps[:3]:event('register_discontinuity','There is an abrupt pitch break within this note — try a gentle, lighter transition.',t[i],'Register Release')
        r.event('register_limit' ,'Register Release describes connected sound only. A range test does not identify your passaggio; no anatomical register or squeeze diagnosis is made.',valence='neutral',timing='Summary')
        bounds,_=note_grid(p,ctx.get('bpm'))
        vals=[]
        for a,b in [(0,5),(5,10),(10,15),(15,20)]:
            v=f.rms[window(bounds[a]+.1,bounds[b]-.1)]
            vals.append(float(np.std(v)/max(np.mean(v),1e-8)) if len(v)>10 else None)
        if all(v is not None for v in vals):
            drop=max(0,np.mean(vals[1::2])-np.mean(vals[::2]))
            metric('Support Through Return',100-180*drop,'Descending RMS steadiness compared with the ascending sections; microphone energy is a support proxy.',descending_extra_cv=float(drop))
            if drop>.15:event('return_support','Energy was less steady on the way down — keep it even through the return.',bounds[5],'Support Through Return')
        track=formant_track(f); valid=np.isfinite(track).all(axis=1)&f.voiced
        first=valid&(t<bounds[10]);second=valid&(t>=bounds[10])
        if np.sum(first)>20 and np.sum(second)>20:
            contrast=float(np.median(track[second,1])/np.median(track[first,1])-1)
            metric('Vowel Brightness Contrast',100*np.clip(contrast/.15,0,1),'F2 contrast between ah and eh is an acoustic proxy, not a vowel identity diagnosis.',f2_relative_change=contrast)
            if contrast<.05:event('vowel_contrast','The second pass did not show a brighter vowel — try a gentle eh after ah.',metric='Vowel Brightness Contrast')
            changes=[]
            for a,b in [(2,4),(12,14)]:
                x=track[valid&(t>=bounds[a])&(t<bounds[a+1])]; y=track[valid&(t>=bounds[b])&(t<bounds[b+1])]
                if len(x)>5 and len(y)>5:changes.append(float(np.linalg.norm(np.median(y,axis=0)-np.median(x,axis=0))))
            if changes:
                r.event('resonance_observation',f'The spectral envelope changed by about {np.mean(changes):.0f} Hz near the upper notes. Listen for an easy adjustment; formant movement alone cannot prove release or forcing.',valence='neutral',timing='Summary')
        else:r.unavailable('Vowel Brightness Contrast','Reliable F1/F2 coverage is insufficient to compare ah and eh.')
        r.unavailable('Resonance Adjustment','Formant movement is reported when measurable, but cannot reliably score natural adjustment versus forcing without a personal baseline.')
        baseline=ctx.get('soft_rms_baseline')
        if baseline and baseline>0:
            level=float(np.median(f.rms[f.voiced]));rise=float(20*np.log10(max(level,1e-9)/baseline))
            metric('Soft Dynamic Match',100-8*max(0,rise-3),'Recorded energy compared with your soft reference on the same microphone; this is not absolute vocal loudness.',above_baseline_db=rise)
            if rise>6:event('too_loud','This take is louder than your soft reference — start lighter while keeping the microphone position unchanged.',metric='Soft Dynamic Match')
        else:r.unavailable('Soft Dynamic','Record an optional soft reference to compare energy using the same microphone and gain.')
    if code=='7.3':
        from engine.ornaments import ornament_rules
        ornament_rules(f,p,ctx,r,root)
    if code=='7.5' and p.get('run_phase'):
        phase=p['run_phase'];bounds,offsets=note_grid(p,ctx.get('bpm'))
        measured=[n for n in (notes or []) if n['error'] is not None]
        stable=sum(n['sd']<45 and abs(n['error'])<80 for n in measured)
        if len(measured)>=4:
            metric('Note Distinctness (Agility)',100*stable/5,'Five separate stable pitch plateaus are expected in this turn.',distinct_notes=int(stable),expected_notes=5)
            if stable<4:event('blurred_run','Keep the notes distinct rather than sliding through the turn.',metric='Note Distinctness (Agility)')
        else:r.unavailable('Note Distinctness (Agility)','Too few confident pitch plateaus were tracked. Repeat the complete turn clearly.')
        log=cents(f.f0,440);valid=f.voiced[1:]&f.voiced[:-1]
        peaks,_=find_peaks(np.where(valid,np.nan_to_num(np.abs(np.diff(log))),0),height=35,distance=12)
        changes=t[peaks+1];changes=changes[(changes>.1)&(changes<f.duration-.1)]
        if len(changes)>=3:
            spacing=float(np.median(np.diff(changes[:4])))
            r.evidence['measured_tempo']={'bpm':60/max(spacing,.05)}
        if phase=='fast':
            slow=ctx.get('slow_take',{});baseline=slow.get('metric_evidence',{}).get('measured_tempo',{}).get('bpm')
            fast=r.evidence.get('measured_tempo',{}).get('bpm')
            slow_error=slow.get('metric_evidence',{}).get('Pitch Accuracy',{}).get('mean_absolute_cents')
            fast_error=r.evidence.get('Pitch Accuracy',{}).get('mean_absolute_cents')
            if baseline and fast and slow_error is not None and fast_error is not None:
                ratio=fast/baseline;loss=max(0,fast_error-slow_error)
                metric('Tempo Progression',min(100,max(0,(ratio-1)*65))*max(0,1-loss/100),'Measured tempo increase compared with your passed slow take, adjusted for pitch-accuracy loss.',speed_ratio=ratio,phase_errors_cents=[slow_error,fast_error])
                if ratio<1.4:event('no_speedup','Keep the turn accurate, then make this pass faster than your slow take.',metric='Tempo Progression')
                if loss>30:event('speed_accuracy','Accuracy dropped at speed — return to slow practice before increasing it.',metric='Tempo Progression')
            else:r.unavailable('Tempo Progression','Both passes need clear separate pitch transitions to compare actual tempo.')
            last=notes[-1] if notes else None
            if last and last['error'] is not None:
                held=min(1,max(0,f.duration-last['start'])/(last['end']-last['start']))
                metric('Landing Clarity',accuracy(abs(last['error']))*held,'Final tonic pitch and held duration.',held_fraction=held,deviation_cents=last['error'])
                if held<.7 or abs(last['error'])>30:event('rushed_landing','Let the final tonic settle and hold it for the full second.',last['start'],'Landing Clarity')
            else:r.unavailable('Landing Clarity','The final tonic was not tracked clearly.')
        return
    if code in {'7.4','7.5'}:
        if code=='7.4':rename('Continuity','Legato Continuity');rename('Vowel Consistency','Vowel Stability')
        bounds,offsets=note_grid(p,ctx.get('bpm'))
        # Find stable note changes using consecutive confident pitch samples.
        log=cents(f.f0,440); smooth=np.array(log)
        for i in range(2,len(log)-2):
            if np.all(f.voiced[i-2:i+3]):smooth[i]=np.median(log[i-2:i+3])
        delta=np.abs(np.diff(smooth));valid=f.voiced[1:]&f.voiced[:-1]
        peaks,_=find_peaks(np.where(valid,delta,0),height=35,distance=12)
        changes=t[peaks+1]
        ratios=[]
        for start,stop in [(0,5),(5,10)]:
            expected=bounds[start+1:stop]
            found=[]
            for at in expected:
                near=changes[np.abs(changes-at)<.4*(bounds[min(start+1,9)]-bounds[start])]
                if len(near):found.append(float(near[np.argmin(abs(near-at))]))
            ratios.append(found)
        # Estimate actual phase spacing independently of the target tempo.
        # This also recognises a repeat that stayed slow instead of speeding up.
        ratios=[changes[(changes>bounds[0]+.1)&(changes<bounds[5]-.1)][:4],
                changes[(changes>bounds[5]+.1)&(changes<f.duration-.08)][:4]]
        if code=='7.4':
            if all(len(x)>=3 for x in ratios):
                slow=np.median(np.diff(ratios[0]));repeat=np.median(np.diff(ratios[1]))
                if repeat<slow*1.06:event('slower_repeat','Slow down on the repeat — this pass was close to the same speed as the first.',metric='Legato Continuity')
            else:r.event('repeat_tempo_uncertain','The second pass tempo could not be measured reliably; listen back to confirm it was slower.',valence='neutral',timing='Summary')
        else:
            measured=[n for n in (notes or []) if n['error'] is not None]
            stable=0
            for n in (notes or [])[5:]:
                if n['error'] is not None and n['sd']<45 and abs(n['error'])<80:stable+=1
            metric('Note Distinctness (Agility)',100*stable/5,'Fast notes need separate stable pitch plateaus; a continuous slide does not count.',stable_fast_notes=stable)
            if stable<4:event('blurred_run','The run is sliding together — keep each pitch separate and clearly articulated.',bounds[5],'Note Distinctness (Agility)')
            if all(len(x)>=3 for x in ratios):
                ratio=float(np.median(np.diff(ratios[0]))/np.median(np.diff(ratios[1])))
                errors=[np.mean([abs(n['error']) for n in measured if a<=n['index']<b]) if any(a<=n['index']<b for n in measured) else 200 for a,b in [(0,5),(5,10)]]
                metric('Tempo Progression',min(100,max(0,(ratio-1)*65))*max(0,1-max(0,errors[1]-errors[0])/100),'Detected slow-to-fast tempo increase, adjusted for loss of pitch accuracy.',speed_ratio=ratio,phase_errors_cents=errors)
                if ratio<1.4:event('no_speedup','This did not get substantially faster on the repeat — establish the slow pattern, then build speed.',metric='Tempo Progression')
                if errors[1]>errors[0]+30:event('speed_accuracy','Accuracy dropped once you sped up — return to the slow pass until it is solid.',metric='Tempo Progression')
            else:r.unavailable('Tempo Progression','Separate note transitions were not clear enough in both phases to measure the speed increase.')
            last=(notes or [])[-1] if notes else None
            if last and last['error'] is not None:
                held=min(1,max(0,f.duration-last['start'])/(last['end']-last['start']))
                metric('Landing Clarity',accuracy(abs(last['error']))*held,'Final tonic accuracy and its held duration were checked.',held_fraction=held,deviation_cents=last['error'])
                if held<.7 or abs(last['error'])>30:event('rushed_landing','Hold the final note clearly — do not let the run trail off.',last['start'],'Landing Clarity')
            else:r.unavailable('Landing Clarity','The final held tonic was not tracked clearly.')
            r.unavailable('Jaw and Tongue Freedom','Audio alone does not establish jaw or tongue tension. Listen for ease and compare the slow and fast passes.')
    if code=='7.6':
        from engine.exercise_analysis import match_grid
        gaps=internal_gaps(f); planned=ctx.get('planned_breaths',[])
        if planned:
            centers=[(a+b)/2 for a,b in gaps]
            pairs=match_grid(centers,planned,.6)
            metric('Breath Planning',100*len(pairs)/max(len(planned),len(gaps),1),'One-to-one matching of recorded pauses and planned breath times; word boundaries are not inferred.',matched_breaths=len(pairs),planned_breaths=len(planned))
            matched={i for i,j in pairs}
            for i,(a,b) in enumerate(gaps):
                if i not in matched:event('unplanned_capstone_breath','This pause was outside your breath plan — listen back and check the phrase boundary.',a,'Breath Planning')
        else:r.unavailable('Breath Planning','Enter planned breath times before recording to compare your pauses with the plan.')
        jumps=[]
        log=cents(f.f0,440)
        for a,b in runs(f.voiced):
            if b-a>15:jumps.extend(np.diff(log[a:b]).tolist())
        if jumps:metric('Pitch Stability',accuracy(np.median(np.abs(jumps))*3),'Local pitch control without a fixed target. Intended melody and vibrato can affect this proxy.',median_local_change_cents=float(np.median(np.abs(jumps))))
        from scipy.ndimage import uniform_filter1d
        from engine.exercise_analysis import _articulation_rules,detect_attacks
        span=(t>=0)&(t<f.duration-.08)
        envelope=uniform_filter1d(f.rms,31)[span]
        db=20*np.log10(envelope+1e-8)
        spread=float(np.percentile(db,90)-np.percentile(db,10))
        # Require a sustained rise and fall, rather than rewarding raw range.
        slope=np.diff(uniform_filter1d(db,31))
        up=float(np.mean(slope>.005));down=float(np.mean(slope<-.005))
        balance=min(1,min(up,down)/.15)
        variation=float(np.median(np.abs(np.diff(db))))
        shape=100*np.clip(spread/6,0,1)*balance*max(.2,1-variation)
        metric('Dynamic Shape',shape,'Smoothed phrase envelope checked for a sustained swell and release, rather than raw volume range alone. Intentional expression needs your listening review.',range_db=spread,rising_fraction=up,falling_fraction=down)
        idx=detect_attacks(f,.12)
        if len(idx)>=4:
            _articulation_rules(f,p,ctx,r)
            rename('Onset Clarity','Diction Clarity')
            r.event('diction_proxy','Diction Clarity measures acoustic attack definition, not word recognition or pronunciation. Listen back to confirm that your words are understandable.',valence='neutral',timing='Summary')
        else:r.unavailable('Diction Clarity','At least four distinct syllable attacks are needed for an acoustic clarity estimate. Word pronunciation still requires listening.')
        rename('Continuity','Legato Continuity')
