import {AbsoluteFill} from 'remotion';

import React, {useMemo} from 'react';
import {
	staticFile,
	useVideoConfig,
	Img,
	Easing,
	Audio,
	useCurrentFrame,
	interpolate,
} from 'remotion';
import imageSequences from './Assets/ImageSequences.json';
import {TransitionSeries, linearTiming} from '@remotion/transitions';

const ImageStream = React.memo(() => {
	const {fps} = useVideoConfig();
	return (
		<AbsoluteFill
			style={{
				top: '50%',
				left: '50%',
				transform: 'translate(-50%, -50%)',
				color: 'white',
				position: 'absolute',
				width: '100%',
				height: '100%',
				zIndex: 0,
				objectFit: 'cover',
			}}
		>
			<TransitionSeries>
				{imageSequences.map((entry, index) => {
					return (
						<>
							<TransitionSeries.Sequence
								key={entry.start}
								durationInFrames={fps * (entry.end - entry.start)}
							>
								<Images key={index} index={index} entry={entry} />;
							</TransitionSeries.Sequence>
						</>
					);
				})}
			</TransitionSeries>
		</AbsoluteFill>
	);
});

const Images = React.memo(({entry, index}) => {
	const frame = useCurrentFrame();
	const {fps} = useVideoConfig();

	const duration = fps * 2.5;
	const ImgScale = interpolate(frame, [1, duration], [1, 1.2], {
		easing: Easing.bezier(0.65, 0, 0.35, 1),
		extrapolateRight: 'clamp',
		extrapolateLeft: 'clamp',
	});

	return (
		<AbsoluteFill
			style={{
				BackgroundColor: 'black',
			}}
			className="bg-black"
		>
			<Audio src={staticFile('sfx_1.mp3')} volume={0.5} />
			<Img
				id="imagex"
				style={{
					scale: 2,
					filter: `url(#blur)`,
					objectPosition: 'center',
					objectFit: 'cover',

					position: 'absolute',
					top: '50%', // Center vertically
					left: '50%', // Center horizontally
					transform: `translate(-50%, -50%) scale(${ImgScale})`,
					width: 1080,
					height: 1920,
				}}
				src={staticFile(entry.name)}
			/>
		</AbsoluteFill>
	);
});

export default ImageStream;
