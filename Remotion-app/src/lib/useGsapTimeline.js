import gsap from 'gsap';
import {useEffect, useRef} from 'react';
import {useCurrentFrame, useVideoConfig} from 'remotion';

export const useGsapTimeline = (gsapTimelineFactory) => {
	const animationScopeRef = useRef(null);
	const timelineRef = useRef();
	const frame = useCurrentFrame();
	const {fps} = useVideoConfig();

	useEffect(() => {
		if (animationScopeRef.current) {
			// check if the component is mounted
			const ctx = gsap.context(() => {
				timelineRef.current = gsapTimelineFactory();
				timelineRef.current.pause();
			}, animationScopeRef);
			return () => ctx.revert();
		}
	}, [animationScopeRef.current]);

	useEffect(() => {
		if (animationScopeRef.current)
			if (timelineRef.current) {
				// check if the component is mounted
				timelineRef.current.seek(frame / fps);
			}
	}, [frame, fps, animationScopeRef.current]);

	return animationScopeRef;
};
