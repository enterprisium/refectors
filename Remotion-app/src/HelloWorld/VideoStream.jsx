import {Series} from 'remotion';
import React from 'react';
import {Video, staticFile, useVideoConfig} from 'remotion';
import videoSequences from './Assets/VideoSequences.json';
import {TransitionSeries} from '@remotion/transitions';

const VideoStream = React.memo(() => {
	const {fps} = useVideoConfig();
	return (
		<TransitionSeries
			style={{
				position: 'absolute',
				zIndex: 1,
			}}
		>
			{videoSequences.map((entry, index) => {
				return (
					<TransitionSeries.Sequence
						key={index}
						from={fps * entry.start}
						durationInFrames={fps * (entry.end - entry.start)}
					>
						<VideoX entry={entry} />
					</TransitionSeries.Sequence>
				);
			})}
		</TransitionSeries>
	);
});

const VideoX = React.memo(({entry}) => {
	const {fps} = useVideoConfig();
	return (
		<Video
            pauseWhenBuffering
			startFrom={(fps * entry.props.startFrom) / 30}
			endAt={(fps * entry.props.endAt) / 30}
			volume={(fps * entry.props.volume) / 30}
			src={staticFile(entry.name)}
		/>
	);
});

export default VideoStream;
