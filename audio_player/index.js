const player = require('play-sound')({})
const pollyPlayer = { player: "blah" };

console.log("AUDIO PLAYER: ","audio player started...");
// print process.argv
const audioFile = process.argv[2];

console.log("AUDIO PLAYER: ",`playing: ${audioFile}`);

player.play(audioFile, function (err) {
    if (err) throw err;
    console.log("AUDIO PLAYER: ","Audio finished");
});
