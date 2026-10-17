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
        if not ctx.get('soft_rms_baseline'):r.unavailable('Soft Dynamic','Microphone gain is uncalibrated; a personal soft-singing baseline is needed to judge absolute loudness.')
    if code=='7.3':
        # Grace/main boundaries are short; pitch plateaus detect legato ornaments
        # that do not produce a separate energy attack.
        bounds, offsets=note_grid(p,ctx.get('bpm')); root=root or measured_pitch(.2,.7)
        clear=[];land=[];beat=[];directions=set()
        for k in range(4):
            a,b,c=bounds[2*k:2*k+3]; grace=measured_pitch(a+.02,b-.02); main=measured_pitch(b+.04,c-.05)
            ok=bool(grace and main and abs(float(cents(grace,main))-offsets[2*k]*100)<80)
            clear.append(ok)
            if ok:directions.add(1 if grace>main else -1)
            else:event('missing_grace','The grace note did not come through distinctly — add a quick extra pitch before the main note.',a,'Grace Note Clarity')
            if main and root:
                err=abs(float(cents(main,root)));land.append(err)
                region=np.flatnonzero(window(a,min(c,b+.3)) & (np.abs(cents(f.f0,root))<35))
                settled=None
                for i in region:
                    if i+4<len(t) and np.all(f.voiced[i:i+4]) and np.all(np.abs(cents(f.f0[i:i+4],root))<35):settled=t[i];break
                if settled is not None:
                    beat.append(abs(settled-b))
                    if settled-b>.15:event('late_main','The grace note is delaying the main beat — borrow time before the beat, then settle on the landing.',settled,'Beat Stability')
                    if settled-a>.25:event('long_grace','The grace note is taking too much time — make it quicker and lighter.',a,'Grace Note Clarity')
        metric('Grace Note Clarity',100*np.mean(clear),'Distinct short pitch and sustained main-note pairs detected.',distinct_pairs=int(sum(clear)),expected_pairs=4)
        if beat:metric('Beat Stability',100-400*np.mean(beat),'Main-note pitch arrival compared with the relative beat grid. Device-clock entrance is not assessed.',mean_arrival_error_seconds=float(np.mean(beat)))
        else:r.unavailable('Beat Stability','No confident main-note arrivals could be matched to the beat grid.')
        if land:metric('Landing Accuracy',accuracy(np.mean(land)),'Held main notes compared with the first confirmed main pitch.',mean_absolute_cents=float(np.mean(land)))
        else:r.unavailable('Landing Accuracy','Main-note plateaus were not clear enough to score landing pitch.')
        if len(directions)<2:event('ornament_direction','Try the grace note from both sides — above the main note, then below it.',metric='Grace Note Clarity')
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
        gaps=internal_gaps(f); planned=ctx.get('planned_breaths',[])
        if planned:
            matches=sum(any(a-.4<=v<=b+.4 for a,b in gaps) for v in planned)
            metric('Breath Planning',100*matches/max(len(planned),len(gaps),1),'Detected pauses compared with your planned breath times; word boundaries are not inferred.',matched_breaths=matches,planned_breaths=len(planned))
        else:r.unavailable('Breath Planning','Enter planned breath times before recording to compare your pauses with the plan.')
        jumps=[]
        log=cents(f.f0,440)
        for a,b in runs(f.voiced):
            if b-a>15:jumps.extend(np.diff(log[a:b]).tolist())
        if jumps:metric('Pitch Stability',accuracy(np.median(np.abs(jumps))*3),'Local pitch control without a fixed target. Intended melody and vibrato can affect this proxy.',median_local_change_cents=float(np.median(np.abs(jumps))))
        db=20*np.log10(f.rms[f.voiced]+1e-8);spread=float(np.percentile(db,90)-np.percentile(db,10))
        metric('Dynamic Shape',100*np.clip(spread/6,0,1),'Recorded dynamic range; musical intention requires your listening review.',range_db=spread)
        r.unavailable('Diction Clarity','Attack definition is an acoustic proxy only; word clarity needs a listening review without aligned lyrics.')
        rename('Continuity','Legato Continuity')
