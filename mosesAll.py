# -*- coding: utf-8 -*-
#This file creates a chart of chords, chosen according to a pitch-dependent probability table, for a carillon with an arbitrary range.
#Next, it became primarily the code that avoids ledger lines via additional staves. 1/27/13
#Possible model: default behavior is piano staff; octave_treble = True, octave_bass = True, splits = 
#returns "piano_staff" containing n staffs.

#all three staffs present.

from abjad import *
from random import randint, seed, choice
import os

#seed the random number generator
seed(1)

#layout and formatting - global 
    
    
def make_piano_staff():
    piano_staff = scoretools.PianoStaff()
    top_staff = Staff()
    top_staff.name = "top"
    bottom_staff = Staff()
    bottom_staff.name = "bottom"
    contexttools.ClefMark('bass')(bottom_staff)
    piano_staff.extend([top_staff, bottom_staff])
    marktools.LilyPondCommandMark('override StaffGrouper.staffgroup-staff-spacing.basic-distance = #200')(piano_staff[0])
    return piano_staff

def make_staff_line_position_override_mark( clef_key ):
    #makes a LilyPondCommandMark that moves the staff lines according to a clef_key.
    #clef_key: 1 - 15va treble; 2 - normal treble; 3 - bass; 4 - treble and bass
    clef_dictionary = {1: schemetools.Scheme(18, 16, 14, 12, 10), 2: schemetools.Scheme(4, 2, 0, -2, -4), 3: schemetools.Scheme(-8, -10, -12, -14, -16), \
    4: schemetools.Scheme(4, 2, 0, -2, -4, -8, -10, -12, -14, -16)}
    staff_lines_scheme = clef_dictionary[clef_key]
    mark_string = "override Staff.StaffSymbol #'line-positions = #'" + str(staff_lines_scheme)
    staff_position_mark = marktools.LilyPondCommandMark(mark_string)
    return staff_position_mark

def make_clef_symbol_change_tuple( clef_key):
    #given a clef_key, returns a tuple of the three marks required to set clef symbol, position, and octavation.
    clef_glyph_dictionary = {1: ["#\"clefs.G\"", 12, 14], 2: ["#\"clefs.G\"", -2, 0], 3: ["#\"clefs.F\"", -10, 0], 4: ["#\"clefs.F\"", -10, 0] }
    glyph_list = clef_glyph_dictionary[ clef_key ]
    clef_symbol_string = glyph_list[0]
    position = "#" + str(glyph_list[1] )
    octavation = "#" + str(glyph_list[2] )
    return (clef_symbol_string, position, octavation)

def move_staff_lines(leaf, clef_key):
    #use: switches the position of staff lines at leaf according to clef_key (see above for description of key system)
    #algorithm: 
    #1. restarts staff
    #2. looks up clef symbol, position, and octavization in dictionary; attaching those marks to leaf 
    #3. attaches staff line position change to leaf
    marktools.LilyPondCommandMark("stopStaff")(leaf)
    marktools.LilyPondCommandMark("startStaff")(leaf)
    staff_position_mark = make_staff_line_position_override_mark( clef_key )
    staff_position_mark.attach(leaf)
    clef_symbol_change_tuple = make_clef_symbol_change_tuple( clef_key )
    symbol_string = clef_symbol_change_tuple[0]
    position = clef_symbol_change_tuple[1]
    octavation = clef_symbol_change_tuple[2]
    clef_string = "set Staff.clefGlyph = " + symbol_string
    marktools.LilyPondCommandMark(clef_string)(leaf)
    marktools.LilyPondCommandMark("set Staff.clefPosition = " + position)(leaf)
    marktools.LilyPondCommandMark("set Staff.clefOctavation = " + octavation)(leaf)

def format_staff( staff ):
    #staff.override.time_signature.stencil = False
    staff.override.beam.damping = schemetools.Scheme('+inf.0')
    staff.set.explicit_clef_visibility = schemetools.Scheme("end-of-line-invisible")
    staff.override.beam.breakable = True
    for x, voice in enumerate(staff[1:]):
        if x % 2 == 1:
            marktools.LilyPondCommandMark('break', 'after')( voice[-1])

def format_score(score):
    score.set.proportional_notation_duration = schemetools.SchemeMoment(1,32)
    score.set.tuplet_full_length = True
    score.override.spacing_spanner.uniform_stretching = False
    score.override.spacing_spanner.strict_note_spacing = False
    score.set.tuplet_full_length = False
    score.override.tuplet_bracket.padding = 1.5
    score.override.tuplet_bracket.staff_padding = 1.5
    score.override.tuplet_number.text = schemetools.Scheme('tuplet-number::calc-fraction-text')
    #score.override.bar_number.transparent = True
    score.override.metronome_mark.padding = 2
    
def format_lilypond_file(lilypond_file):
    lilypond_file.paper_block.paper_width = 11 * 25.4
    lilypond_file.paper_block.paper_height = 8.5 * 25.4
    lilypond_file.paper_block.top_margin = 1.0 * 25.4
    lilypond_file.paper_block.bottom_margin = 0.5 * 25.4
    lilypond_file.paper_block.left_margin = 1.0 * 25.4
    lilypond_file.paper_block.right_margin = 1.0 * 25.4
    lilypond_file.paper_block.ragged_bottom = False
    lilypond_file.global_staff_size = 12
    lilypond_file.layout_block.indent = 0
    lilypond_file.layout_block.ragged_right = False
    lilypond_file.paper_block.system_system_spacing = layouttools.make_spacing_vector(0, 0, 20, 0)
    directory = os.path.dirname(os.path.abspath(__file__))
    fontTree = os.path.join(directory,'fontTree.ly')
    lilypond_file.file_initial_user_includes.append(fontTree)

#layout and formatting - local

def format_melody(melody):
    marktools.LilyPondCommandMark('break','after')(melody[-1])
    contexttools.TempoMark((1,4), 50)(melody[0])
    contexttools.DynamicMark('f')(melody[0])
    marktools.BarLine('||')(melody[-1])

#staff and clef moving:

def add_staff_switches_to_voice( voice ):
    move_staff_lines_at_leaf(voice[0], 1)
    notes = list( iterationtools.iterate_notes_in_expr( voice ) )
    treble_notes = [x for x in notes if x.sounding_pitch.pitch_number < 24 and x.sounding_pitch.pitch_number >= -1]
    move_staff_lines_at_leaf(treble_notes[0], 2)
    bass_notes = [x for x in notes if x.sounding_pitch.pitch_number < 0]
    move_staff_lines_at_leaf(bass_notes[0], 3)

def format_voice( voice ):
    contexttools.TimeSignatureMark((1,16))( voice[0] )
    spannertools.PhrasingSlurSpanner( voice[:])
    beamtools.BeamSpanner( voice[:] )
    add_staff_switches_to_voice( voice )
    voice.override.phrasing_slur.ratio = 0.6
    voice.override.phrasing_slur.height_limit = 20
    

#composition
def choose_distance_from_range_low(seed_interval):
    interval_width = seed_interval.number
    choice = randint(0, interval_width)
    return choice
    
def get_pitch_set_from_pitch_range_tuple( pitch_range_tuple ):
    numeric_pitch_range_tuple = (numeric_pitch_range_low, numeric_pitch_range_high)
    pitches = [ ]
    for value in range( numeric_pitch_range_tuple[0], numeric_pitch_range_tuple[1] ):
        pitch = NamedPitch(value)
        pitches.append(pitch)
    return pitches

def make_chord( bottom_pitch_number, numeric_pitch_range_high ):
    pitch_number = bottom_pitch_number
    bottom_pitch = NamedPitch( pitch_number  )
    bottom_interval_choices = [5, 7, 9]
    chord = Chord( [ bottom_pitch ], Duration(1,4) )
    bottom_interval_ambitus = choice(bottom_interval_choices)
    next_to_bottom_pitch = bottom_pitch + bottom_interval_ambitus
    chord.append( next_to_bottom_pitch )
    added_pitch = next_to_bottom_pitch
    while added_pitch.pitch_number <= int(numeric_pitch_range_high * 2/3) :
        #pitch = choose_pitch_from_weighted_table(pitch)
        sizes = [ 3, 4 ]
        interval_size = choice(sizes)
        current_pitch = added_pitch + interval_size
        chord.append( current_pitch  )
        added_pitch = current_pitch
    while added_pitch.pitch_number <= int(numeric_pitch_range_high) :
        #pitch = choose_pitch_from_weighted_table(pitch)
        sizes = [ 1, 2 ]
        interval_size = choice(sizes)
        current_pitch = added_pitch + interval_size
        chord.append( current_pitch  )
        added_pitch = current_pitch
    return chord   

def make_chords(number_of_chords, pitch_range_tuple):
    #numeric_pitch_range_low = pitchtools.chromatic_pitch_name_to_pitch_number( pitch_range_tuple[0] )
    numeric_pitch_range_low = NamedPitch(pitch_range_tuple[0]).pitch_number
    #numeric_pitch_range_high = pitchtools.chromatic_pitch_name_to_pitch_number( pitch_range_tuple[1] )
    numeric_pitch_range_high = NamedPitch(pitch_range_tuple[1]).pitch_number
    chords = [ ]
    for x in range(number_of_chords):
        distance_from_range_low = choose_distance_from_range_low( pitchtools.NumberedInterval(7) )
        bottom_pitch_number = numeric_pitch_range_low + distance_from_range_low
        chord = make_chord( bottom_pitch_number, numeric_pitch_range_high )
        chords.append(chord)
    return chords

#def place_component_on_staffs(component, braced_staffs):
 #   #if 1 < len(component):
  #   #   place_tuplet_on_staffs( component, braced_staffs )
  #  elif isinstance(component, Rest):    
  #      place_rest_on_staffs(component, braced_staffs)
  #  elif isinstance(component, Note):
  #      place_note_on_staffs(component, braced_staffs)
  #  elif isinstance(component, Chord):
  #      place_note_on_staffs(component, braced_staffs) 

def get_range_bounds( voice ):
    pitch_numbers = [ x.written_pitch.pitch_number for x in iterationtools.iterate_components_and_grace_containers_in_expr( voice.leaves, (Note, Chord) ) ]
    low = min(pitch_numbers)
    high = max(pitch_numbers)
    return (low, high)

def make_score( staff ):
    score = Score( [staff] )
    format_score(score)
    return score

def make_lilypond_file( staff ):
    score = make_score( staff )
    lilypond_file = lilypondfiletools.make_basic_lilypond_file(score)
    format_lilypond_file(lilypond_file)
    return lilypond_file

def make_chord_chart(number_of_chords, pitch_range_tuple):
    chords = make_chords(number_of_chords, pitch_range_tuple)
    lilypond_file = make_lilypond_file(chords)
    show(lilypond_file)
    play(lilypond_file)

def arpeggiate_chord( chord ):
    notes = [ ]
    pitches = chord.written_pitches
    ordered_pitches = [ ]
    for pitch in pitches:
        ordered_pitches.append( pitch )
    ordered_pitches.reverse()
    for pitch in ordered_pitches:
        note = Note(pitch, Duration(1,16))
        notes.append( note )
    voice = Voice(notes)
    #format_voice(voice)
    return voice

def color_pitch( arpeggio, pitch):
    for note in iterationtools.iterate_notes_in_expr(arpeggio):
        if pitch == note.sounding_pitch:
            note.override.note_head.color = "red"
        

def contains_pitch( pitch_to_find, arpeggio ):
    pitches = set(pitchtools.list_named_chromatic_pitches_in_expr(arpeggio))
    if pitches.issuperset([ pitch_to_find ] ):
        return True
        
def format_subsequent_pitch( arpeggio, note, hidden_melody_tuple ):
    melody_note_dynamic = hidden_melody_tuple[1]
    original_dynamic = hidden_melody_tuple[0]
    marktools.Articulation("-",Up)(note)
    contexttools.DynamicMark(melody_note_dynamic)(note)
    index_of_the_note_after_that = note.parent.index(note)
    if index_of_the_note_after_that < len( arpeggio ) - 1:
        note_after_that = componenttools.get_nth_sibling_from_component(note, 1)
        contexttools.DynamicMark(original_dynamic)(note_after_that)

def emphasize_pitch( arpeggio, pitch_to_check, hidden_melody_tuple):
    for note in iterationtools.iterate_notes_in_expr(arpeggio):
        if pitch_to_check == note.sounding_pitch:
            format_subsequent_pitch( arpeggio, note, hidden_melody_tuple )
    
def find_melody_in_arpeggios( melody, arpeggio_voices, nth_time ):
    nth_time_dictionary = {0: [24, 'ppp', 'mf'], 1: [12, 'p', 'f'], 2: [0, 'mf', 'ff']}
    hidden_melody_tuple = nth_time_dictionary[nth_time]
    hidden_melody_transposition = hidden_melody_tuple[0]
    hidden_melody_tuple = hidden_melody_tuple[1:]
    selected_arpeggios = [ ]
    pitches = [ x.sounding_pitch for x in iterationtools.iterate_notes_in_expr( melody )]
    pitch_index = 0
    for arpeggio in arpeggio_voices:
        if pitch_index == len(pitches):
            break
        pitch_to_check = pitches[ pitch_index] + hidden_melody_transposition
        if contains_pitch( pitch_to_check, arpeggio):
            contexttools.DynamicMark(hidden_melody_tuple[0])(arpeggio[0])
            selected_arpeggios.append( arpeggio )
            #color_pitch( arpeggio, pitch_to_check)
            emphasize_pitch( arpeggio, pitch_to_check, hidden_melody_tuple)
            pitch_index += 1
    return selected_arpeggios
        
def arpeggiate_chords( chords ):
    arpeggio_voices = [ ]
    for chord in chords:
        arpeggio_voice = arpeggiate_chord( chord )
        arpeggio_voices.append( arpeggio_voice )
    return arpeggio_voices

def get_n_pitches_above_note_in_chord(note, chord, division):
    pitches = [x.written_pitch for x in chord if x.written_pitch.pitch_number > note.written_pitch.pitch_number]
    return pitches[ :division ]

def shift_pitches(pitches):
    shifted_pitches = []
    for pitch in pitches:
        pitch -= 12
        shifted_pitch = NamedPitch(pitch)
        shifted_pitches.append(shifted_pitch)
    shifted_pitches.reverse()
    return shifted_pitches
    
def pitch_tuplet(tuplet, note_chord_pair, division, x):
    note = note_chord_pair[0]
    chord = note_chord_pair[1]
    pitches = get_n_pitches_above_note_in_chord(note, chord, division)
    tuplet[0].written_pitch = note.written_pitch
    marktools.Articulation(">")(tuplet[0])
    note_pitch_pairs = zip(tuplet[1:], pitches)
    if x % 2 == 1:
        shifted_pitches = shift_pitches(pitches)
        note_pitch_pairs = zip(tuplet[1:], shifted_pitches)
    for pair in note_pitch_pairs:
        note = pair[0]
        pitch = pair[1]
        note.written_pitch = pitch
    
def split_melody(melody, division, chords):
    voice = Voice([Note(melody[0])])
    chords = chords[ : len(melody) ]
    note_chord_pairs = zip( melody[1:], chords )
    ratio = [1] * division
    for x, pair in enumerate(note_chord_pairs):
        duration = inspect(pair[0]).get_duration()
        tuplet = Tuplet.from_duration_and_ratio(duration, ratio)
        pitch_tuplet(tuplet, pair, division, x)
        voice.append(tuplet)
    marktools.BarLine('||')(voice[-1])
    return voice
        

def vary_melody( melody, divisions, chords ):
    voices_to_add = []
    for division in divisions:
        voice_to_add = split_melody(melody, division, chords )
        voices_to_add.append( voice_to_add)
    return voices_to_add
    
def make_transition_from_run( melody_one, decorated, run ):
    voice = Voice([])
    for x,choice in enumerate(run):
        if choice == 0:
            note = Note(melody_one[x])
            voice.append(note)
        elif choice == 1:
            source_tuplet = decorated[x]
            tuplet_leaves = mutate(source_tuplet[:]).copy()
            tuplet = Tuplet(source_tuplet.multiplier, tuplet_leaves)
            voice.append(tuplet)
    marktools.BarLine('||')(voice[-1])
    return voice

def make_moses_all(melody_one, melody_two, pitch_range_tuple):
    chords = make_chords(100, pitch_range_tuple)
    staff = make_piano_staff()
    format_melody(melody_one)
    staff[0].append(melody_one)
    divisions = [3,5,7]
    melody_one_varied = vary_melody( melody_one, divisions, chords)
    not_yets = []
    one = [0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 1, 0, 1]
    two = [0, 0, 1, 0, 1, 0, 1, 1, 0, 0, 1, 1, 1, 1]
    three = [0, 0, 1, 1, 1, 0, 1, 0, 1, 1, 1, 1, 1, 1]
    transition = [one, two, three]
    for run in transition:
        transition_voice = make_transition_from_run( melody_one, melody_one_varied[0], run )
        not_yets.append(transition_voice)
    staff[0].extend(not_yets)
    #second = Voice([melody_one[:1], first_variation[6:8], melody_one[3:6], first_variation[18:21], melody_one)
    staff[0].extend(melody_one_varied)
    contexttools.DynamicMark('p')(melody_two[0])
    staff[0].append(melody_two)
    melody_two_varied = vary_melody(melody_two, divisions, chords[14:])
    not_yets_two = []
    for run in transition:
        transition_voice = make_transition_from_run( melody_two, melody_two_varied[0], run )
        not_yets_two.append(transition_voice)
    staff[0].extend(not_yets_two)
    staff[0].extend(melody_two_varied)
    skips = skiptools.Skip("s1")*112
    staff[1].extend(skips)
    for note in staff[0].select_leaves( allow_discontiguous_leaves=True ):
        if note.written_pitch.pitch_number < 0:
            marktools.LilyPondCommandMark('change Staff = \"bottom\"', 'before')(note)
        else:
            marktools.LilyPondCommandMark('change Staff = \"top\"', 'before')(note)
    staff[1].override.beam.damping = schemetools.Scheme('+inf.0')
    marktools.BarLine('|.')(staff[0][-1])
        
    #process
    #for x in range(3):
    #    nth_time = x
    
    #    arpeggio_voices = arpeggiate_chords( chords )
    #    selected_voices = find_melody_in_arpeggios( melody, arpeggio_voices, nth_time )
    #    staff.extend(selected_voices)
    format_staff(staff[0])
    lilypond_file = make_lilypond_file( staff )
    show(lilypond_file)
    #play(lilypond_file)

melody_one = Voice("d'1 df'4 a'2. c'2 a' b2. a'4 bf1 a4 a'2. a2 a' a2. a'4")
melody_two = Voice("d'1 e'4 cs'2. fs'2 cs' fs'2. gs'4 b1 a4 a'2. a2 a' a2. a'4")
make_moses_all( melody_one, melody_two, ("c", "c''''") )