import sqlite3

from misc_files import common_vars


def tag_importer():
	fxTags = {
		'No effects': 'This should be checked if this video uses no effects.\nBecause of their ubiquity, crossfades and time stretching/\n' + \
		              'compression are not considered "effects", however any-\nthing beyond that should be represented by one or more\nof the effects tags below.',

		'2.5D camera': 'This is a colloquial term used to describe an effect whereby\nthe editor basically takes the camera and moves it around\n' + \
		        'in 3D space, but all the subjects within the shot are 2D\nobjects. This is separate from other "camera" effects below\n' + \
		        'in that the camera actually moves three-dimensionally,\noften pivoting on its axes rather than just panning/zooming\n' + \
		        'along them.',

		'3D animation': 'This tag denotes a video which features editor-created 3D\nanimation. This must be original work, and this tag should\n' + \
		      'not be selected for 3D animation that is featured within an\nanime, or other professionally-created content used within\n' + \
		      'the video.',

		'60 fps': 'These videos are those which have used some third-party\nframe-interpolation software or plugin (most commonly\n' + \
		          'Twixtor) to add frames to the source material, bringing\nit up to 60 frames per second. Since currently no or\n' + \
		          'few anime are rendered natively at 60 fps, some editors\nartificially create this in their videos. This typically\n' + \
		          'lends the video a trademark "smooth" feel, while at the\nsame time often creating unintentionally surreal and\n' + \
		          'wonky movement (as frame-interpolation software often\nhas trouble properly rendering animated sources).',

		'Blurs': 'Any time a video makes use of editor-added blurring effects,\nthis tag should be selected. This includes not just Gaussian\n' + \
		         'blurs, but linear, radial, and depth-of-field blurs as well.',

		'Burn': 'The burn effect simulates the video being burned like a piece\nof paper; it appears as dark charring around the edges and in\n' + \
		        'the middle of the frame which grow and leave "holes" in the\nvideo, until there is nothing left. This is most commonly used\n' + \
		        'as a transition technique.',

		'Camera motion': 'This should be selected whenever there is artificially-\nadded camera sway or other gradual, more "natural"\n' + \
		                 'motion (such as pans). This is NOT the same as "camera\nshake", which indicates much more rapid movement.',

		'Camera shake': 'This tag denotes editor-added "shake", or rapid camera\nmovement intended to simulate a camera being shaken\n' + \
		                'by some external force. This is most commonly seen in\nthe form of quick, small camera pans across a short period\n' + \
		                'of time, often used as a sync device, but may also be put\nin effect for a more prolonged period to represent chaos.',

		'Camera zoom': 'Whenever an editor adds his or her own zooms to the video,\nthis tag should be selected. These can be zoom-ins or zoom-\n' + \
		               'outs, and they can be at any speed.',

		'Color correction': 'Color correction is a technique where an editor will\ntweak the colors, highlights, contrast, etc. of a scene in\n' + \
		                    'order to make the scene look more natural. The vast\nmajority of times this effect is seen is in "crossover" and\n' + \
		                    '"new world" videos where editors occasionally take\nmultiple disparate-looking sources, and must color-\n' + \
		                    'correct elements from different masked portions of the\nseparate anime to make them fit together more organically.',

		'Color manipulation': 'This is a very general tag used to indicate any kind of\ncolor work that happens in a video. This can take many\n' + \
		               'different forms -– desaturation, hypersaturation, tone\nadjustments, solid color stills or cutouts used as accents\n' + \
		               'in the background of a video, light leaks, etc.',

		'Compositing': 'Compositing is the act of putting together two or more\nelements that are not already together in the source\n' + \
		               'material. While this doesn\'t necessarily require more\nthan one anime to do, it almost always has them -–\n' + \
		               'and it usually requires extensive masking and color\ncorrection to pull off convincingly. This is, essentially,\n' + \
		               'when an editor creates his own scene using characters\nor objects from separate scenes by masking them out\n' + \
		               'and "compositing" them together.',

		'Cookie': 'A general term for whenever there is a geometric cut-out\noverlaid on top of a scene. This effect was popularized by\n' + \
		          'Koopiskeva\'s video Euphoria, and is sometimes better known\nas the "piano keys" effect.',

		'Film': 'This tag refers to any kind of TV or film effect/filter put on\na video source. This includes dust particles, film grain, static,\n' + \
		        'TV scanning, VCR degradation, and anything else that might\nbe artificially recreating a similar effect.',

		'Glows': 'A glow would be defined as an effect which brightens and accentuates\nthe highlights of a scene, and softens them to make a muted, dreamy\n' + \
		         'radiance.',

		'Grunge': 'The "grunge" tag should be chosen for a video which uses harsh,\ndirty brush stroke overlays to give the video a gritty feel.',

		'HUD': 'Short for "heads-up display", a term used in gaming and other\narenas, but also applicable here to videos that display an editor-\n' + \
		       'created static overlay that shows various data or text. In video\ngame terms, this would be the information scattered around the\n' + \
		       'screen which displays your health, ammo, chosen weapon, etc.\nWhile it doesn\'t have to show this kind of information specifically,\n' + \
		       'it should display something of the sort that probably would\napply more directly to the given video\'s concept.',

		'Kaleidoscope': 'This is an effect that mimics what it\'s like to look into a\nkaleidoscope -– lots of mirrored images at crazy angles,\n' + \
		          'which give the video a confusing, psychedelic look.',

		'Keying': '"Keying" is a type of effect found in most mid-grade and higher\nediting programs, which allows the editor to select a color and\n' + \
		          '"key" it out, or remove it, to display the video track underneath.\nThis is usually a very distinct effect, as it tends to leave behind\n' + \
		          'artifacts which flicker on and off (due to the scene changing color\nenough as it progresses to bring parts of the keyed-out portions\n' + \
		          'back into view) and extremely jagged edges where the keyed\nsection ends.',

		'Lens flare': 'An effect which generates a point of light and mimics the\nflaring and distortion of that light hitting the camera lens.',

		'Light rays': '"Light rays" is an effect whereby a portion of a scene\nappears to have soft, glowy rays protruding off if it,\n' + \
		              'either laterally or (more commonly) appearing to come\n"out" of the screen. This is commonly used to make a\n' + \
		              'dreamy effect.',

		'Masking': 'a.k.a "rotoscoping", and perhaps better-known by that phrase,\nthis describes the technique where an editor will "cut out" a\n' + \
		           'character or object to be used in any number of ways -– as a\nway to do crossover videos, to transition between scenes, to\n' + \
		           'make color adjustments to the background scene, to add\nobjects that serve to add depth or to "decorate" the scene,\n' + \
		           'etc. This is one of the most tedious effects in AMV editing\nbecause of its frame-by-frame adjustment nature, and yet\n' + \
		           'is considered by many editors to be a staple technique in their\nown personal editing styles.',

		'Motion graphics': '"Motion graphics" refers to typically high-quality,\neditor-created graphical images that are added into\n' + \
		                   'the video and have motion applied. This is most fre-\nquently seen in the real world in TV advertisements\n' + \
		                   'and sports broadcasts, i.e. logos or abstract designs\nused to supplement information shown on-screen,\n' + \
		                   'etc.',

		'Motion tracking': 'This tag should be used whenever an image –- user-created\nor not –- is overlaid on top of a scene and moves (or "tracks")\n' + \
		                   'with some element of the scene. An example would be an\neditor overlaying some masked sunglasses on top of a char-\n' + \
		                   'acter\'s face, and making sure the sunglasses move with the\ncharacter so it looks like she\'s wearing them as she walks.',

		'Overlays': 'An "overlay" is an instance where the editor puts one or\nmore video tracks on top of each other, and reduces the\n' + \
		            'opacity of the layers on top to create an effect of\nmultiple scenes being played at once in the same physical\n' + \
		            'space on the screen. Although overlays can also be defined\nas any object or masked element being placed on top\n' + \
		            'of a scene (without an opacity adjustment), those instances\nshould be covered by one or more other FX tags, and\n' + \
		            'those tags should be chosen instead.',

		'Particles': 'The "particles" tag denotes an effect where the editor\nadds in particles through a third-party plugin -– particles\n' + \
		             'being individual objects that are duplicates of one\nanother (often of differing sizes) which usually generate\n' + \
		             'from a single point on the screen, which can itself\nbe moved around. The particles themselves don\'t have\n' + \
		             'to be any specific shape, but are commonly seen as\nsmall circles or spheres of light that fly out from a\nsingle point.',

		'Picture-in-picture': 'An effect where a scene is overlaid on top of the main\nscene in a video (without any opacity adjustment), and\n' + \
		       'both are played at the same time. Sometimes this is\nseen as a smaller image placed in the corner of the\n' + \
		       'video, other times the scene on top covers most of the\nvideo, and only the edges of the video beneath can be\n' + \
		       'seen.',

		'Pixelation': 'An effect where the video or a portion of a scene\nwithin the video is purposely "pixelated" to look\n' + \
		              'as if it is lower quality.',

		'Psychedelia': 'This effect is characterized by one or more of a\nfew possible things –- lots of editor-manipulated\n' + \
		               'color adjustments that happen in rapid succession,\nwavy/ripple effects, kaleidoscopic effects, or any-\n' + \
		               'thing else that might simulate an LSD trip.',

		'Quality distortion': 'Similar to "pixelation", but more general -– this\nrefers to instances of the deliberate lowering of\n' + \
		                'a video\'s quality, often to either achieve a desired\naesthetic or to accentuate some conceptual goal\n' + \
		                'on the part of the editor. This is also sometimes\nseen as a side-effect of Twixtor-enhanced videos\n' + \
		                '(see the "60 fps" tag).',

		'RGB split': 'Use of this effect splits the color of a scene into red,\ngreen, and blue. This is typically demonstrated by the\n' + \
		             'actual scene splitting into three separate lowered-\nopacity overlays that are slightly offset from one\n' + \
		             'another, then merging back together to form the\nnormally-colored scene. This is almost always used\n' + \
		             'as a quick beat sync device, rather than in any\nprolonged manner.',

		'Ripple': 'An effect which contorts the scene and gives it a faux-3D\nlook that simulates waves or ripples on the water. Does\n' + \
		          'not have to be exemplified by circular ripples, but can be\nany shape so long as the same general effect is demon-\nstrated.',

		'Shatter': 'A stock effect which "shatters" the scene into multiple\npieces like broken glass. Its most common use is as a\n' + \
		           'transition.',

		'Split screen': 'An effect where multiple scenes are laid next to each other\nand play simultaneously, but do not cover one another.',

		'Stock filters': 'Stock filters/effects are found in all video editing\nprograms, and are the basis off of which many\n' + \
		                 'effects are created. Use of this tag denotes a video\nwhich uses these stock filters with little adjustment\n' + \
		                 'away from the defaults, or without combination with\nother stock effects which might make the effect\n' + \
		                 'look more "custom"; after watching videos and editing\nfor a little time, it becomes clear when these effects\n' + \
		                 'are being used, sometimes to the point where one can\npinpoint the editing program used without knowing\n' + \
		                 'ahead of time.',

		'Stock transitions': 'Most editing programs ship with default transitions\nbesides the hard cut and crossfade, and this tag should\n' + \
		                     'be selected on those videos that use these out-of-the-\nbox transitions without any adjustment. The stereo-\n' + \
		                     'typical stock transition is the "star wipe", but there\nare many others in the world of AMVs that have become\n' + \
		                     'infamous, including transitions that utilize color manip-\nulation, other geometrical wipes, slides, faux-3D\n' + \
		                     'stuff, and plenty of others. Like the "stock filters" tag,\nthese are easy to spot after spending just a little time\n' + \
		                     'with AMVs and editing.',

		'Text': 'Simply placing text on a video is not enough to earn\nthis tag, there should be some sort of effect associated\n' + \
		        'with it –- motion, the text being "drawn" into existence,\ncolor cycling, etc.',

		'Textures': 'The "textures" tag denotes a video that uses brush\nstrokes or other overlays to lend the video a more\n' + \
		            'textured, three-dimensional quality.',

		'Vectors': '"Vectors" are when an editor masks out a character or\nobject, and fills that mask with a solid color. This creates\n' + \
		           'silhouettes that can be used in all sorts of situations.\nThis can also more generally apply to geometric shapes\n' + \
		           'introduced into the video, so long as they retain a clean,\nslick feel, and this is often combined with motion\n' + \
		           'graphics –- examples of videos that make extensive use of\nthis would be Skittles by Koopiskeva or Boxxed by\n' + \
		           'AimoAio.',

		'Warp': 'Not to be confused with the "ripple" tag, "warp" indicates\nan effect that distorts, twists, or skews the video, very\n' + \
		        'often along or around a point or linear path.',

		'Waveform': 'This describes a generated effect that mimics an audio\nwaveform (either the bouncing columns or a lightning-\n' + \
		            'like line that deforms in time with the audio). The wave-\nform object in the AMV does not necessarily need to\n' + \
		            'sync with the audio, so long as it is present in some\ncapacity this tag should be selected.',
	}

	tag_list = [(k, v.replace('-\n', '').replace('\n', ' ')) for k, v in fxTags.items()]
	sorted(tag_list, key=lambda x: x[0])

	conn = sqlite3.connect(common_vars.tag_db())
	cursor = conn.cursor()
	cursor.executemany('INSERT INTO tags_3 VALUES (?, ?)', tag_list)
	conn.commit()
	cursor.close()


tag_importer()
