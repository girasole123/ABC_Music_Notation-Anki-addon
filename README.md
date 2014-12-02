ABC Music Notation (music integration addon for Anki 2)
=======================================================

ABC Notation is a system designed to notate music in plain text format. <a href="http://abcnotation.com" rel="nofollow">http://abcnotation.com</a>

With this addon, you can add music snippets to your deck, wrapped in <code>[abc]c d e[/abc]</code> tags, and they will be converted to a MP3 music files.

For this addon to work, you have to install <b>abc2midi</b>, <b>timidity</b> and <b>lame</b> first and they need to be in your <i>PATH</i>.

<ul>
<li><b>abc2midi</b> download page: <a href="http://abcplus.sourceforge.net/#abcmidi" rel="nofollow">http://abcplus.sourceforge.net/#abcmidi</a> (alternatively on Ubuntu <code>apt-get install abcmidi</code>)</li>
<li><b>timidity</b> download page: <a href="http://timidity.sourceforge.net/#download" rel="nofollow">http://timidity.sourceforge.net/#download</a> (alternatively on Ubuntu <code>apt-get install timidity</code>)</li>
<li><b>lame</b> download page: <a href="http://lame.sourceforge.net/download.php" rel="nofollow">http://lame.sourceforge.net/download.php</a> (alternatively on Ubuntu <code>apt-get install lame</code>)</li>
</ul>

How to use
----------

This addon understands <code>[abc]</code> tags:<br/>
<code>[abc]c d e[/abc]</code>

Alternatively, you can create dedicated fields, e.g. <i>front-abc</i> or <i>back-abc</i>, and omit the <code>[abc]</code> tags for them:<br/>
<code>c d e</code>

With <i>abc</i> in the field name, it will act as if the entire field content was wrapped in <code>[abc][/abc]</code> tags.

This addon allows the creation of custom templates (see below), and specifying which template to use:<br/>
<code>[abc=default]c d e[/abc]</code><br/>
<code>[abc=yourtemplate]c d e[/abc]</code>

The name of the default template is <i>default</i>, so <code>[abc=default]</code> is identical to <code>[abc]</code>.

You can also use templates in <i>abc</i> fields by giving them names like <i>front-abc-yourtemplate</i>, <i>back-abc-yourtemplate</i>.

Mobile/Web support
------------------

Anki addons are desktop only, so by default, images won't appear on other platforms since those platforms won't know what to make of a <code>[abc]</code> tag or how to treat a <i>abc</i> field.

However, if you are using <i>abc</i> fields, and for each field create another field called <i>abcsnd</i>, the desktop addon will automatically fill it with the <code>[sound]</code> tag.

For example, if your field is <i>front-abc</i>, with content <code>c d e</code>, and you have another field <i>front-abcsnd</i>, and use only the <i>front-abcsnd</i> field in your card template, the sound will appear on all platforms (provided that the desktop addon generated the MP3 file once and the MP3 files were synced to the other platforms as well).

Note: If you add text to a <i>abcsnd</i> field, it will be overwritten and discarded by the addon.

ABC Templates
-------------

The <b>addons/abc</b> directory holds template files for ABC Notation. Templates can be created and edited from within Anki, using the Tools-&gt;abc menu.

Please restart Anki when you change templates.

The default template is <b>default.abc</b> and used by:<br/>
<code>[abc]code[/abc]</code><br/>
<code>[abc=default]code[/abc]</code><br/>
<i>somefield-abc</i>

All other templates have to be specified by name:<br/>
<code>[abc=templatename]code[/abc]</code><br/>
<i>somefield-abc-templatename</i>

In the template, <code>%ANKI%</code> will be replaced with code. Multiple codes can be specified, by separating them with <code>%%%</code>:
<pre>[abc]
code1
%%%
code2
[/abc]</pre>

In the template, the first occurrence of <code>%ANKI%</code> will be replaced with <code>code1</code>, the second occurrence of <code>%ANKI%</code> with <code>code2</code>.

The number of <code>%ANKI%</code> in the template has to match the number of codes used for this template always, otherwise the remaining occurrences of <code>%ANKI%</code> will not be replaced, or the surplus specified codes will not be inserted.

The default template looks like this:
<pre>X:1
M:4/4
L:1/4
K:C
%ANKI%</pre>

If you would like write your own header, you can choose the <i>void</i> template (file template is <b>void.abc</b> and contains only <code>%ANKI%</code>):
<pre>[abc=void]
X:1
T:My own header's title
M:6/8
L:1/8
Q:C8=30
K:F
|: ddc B2 A | AGG F2 D | ddc B2 A | GGF G3 :|
|: AAA c2 c | ccc d2 d | ddc B2 A | GGF G3 :|
[/abc]</pre>
or
<i>somefield-abc-void</i>


Please refer to the ABC Notation homepage and documentation for details on how to write ABC Notation code.

You can also use <code>%%MIDI</code> commands (or <code>[I:MIDI=]</code> inline equivalents) which are particular to the <b>abc2midi</b> program, e.g. <code>%%MIDI drum</code> command (refer to the Guide to Advanced Futures of <b>abc2midi</b>: <a href="http://ifdo.pugmarks.com/~seymour/runabc/abcguide/abc2midi_guide.html" rel="nofollow">http://ifdo.pugmarks.com/~seymour/runabc/abcguide/abc2midi_guide.html</a>).
