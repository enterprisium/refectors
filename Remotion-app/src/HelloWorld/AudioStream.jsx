import {Series} from 'remotion';
import React from 'react';
import {staticFile, useVideoConfig, Audio} from 'remotion';
import audioSequences from './Assets/AudioSequences.json';
import {TransitionSeries} from '@remotion/transitions';
const AudioStream = React.memo(() => {
	const {fps} = useVideoConfig();
	return (
		<TransitionSeries
			style={{
				color: 'white',
				position: 'absolute',
				zIndex: 0,
			}}
		>
			{audioSequences.map((entry, index) => {
				return (
					<TransitionSeries.Sequence
						key={index}
						from={fps * entry.start}
						durationInFrames={fps * (entry.end - entry.start)}
					>
						<AudioX entry={entry} />
					</TransitionSeries.Sequence>
				);
			})}
		</TransitionSeries>
	);
});

const AudioX = React.memo(({entry}) => {
	return (
		<Audio
			{...entry.props}
			// startFrom={entry.props.startFrom}
			// endAt={entry.props.endAt}
			// volume={entry.props.volume}
			src={staticFile(entry.name)}
		/>
	);
});

export default AudioStream;
