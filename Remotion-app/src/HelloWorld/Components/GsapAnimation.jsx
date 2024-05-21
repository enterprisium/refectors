import {useGsapTimeline} from '../../lib/useGsapTimeline';
import {AbsoluteFill} from 'remotion';
import React, {useMemo} from 'react';
import gsap from 'gsap';

const GsapAnimation = React.memo(
	({Timeline, style, className, children, plugins = []}) => {
		const memoizedPlugins = useMemo(() => {
			return [...plugins];
		}, [plugins]);

		gsap.registerPlugin(memoizedPlugins);
		const ContainerRef = useGsapTimeline(Timeline);
		return (
			<AbsoluteFill className={className} style={style} ref={ContainerRef}>
				{children}
			</AbsoluteFill>
		);
	}
);

export default GsapAnimation;
