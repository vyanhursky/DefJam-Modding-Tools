# Extending menu scenery without visible source bounds

Use [the versioned prompt scaffold](../prompts/menu-widescreen-extension.txt)
for future menu backgrounds. Fill every coordinate placeholder from the actual
edit canvas; remove irrelevant material clauses. This is a conversation workflow,
not an automatically wired workshop preset or a runtime wide-texture format.

The skyline pilot exposed a failure that palette checks cannot catch: generated
clouds looked plausible but did not continue the source cloud shapes. The model
also redrew its source reference. Copying back the real center then exposed a
vertical cut. An ambiguous left/right boundary sentence made the brief weaker.

1. Join source tiles using proven UV placement. Establish the exact protected
   original and source-to-stage transform before extending any layer.
2. Supply the final canvas with the actual protected original already in place.
   Keep enough context to see cloud trajectories or other large structures.
   Treat the original as fixed. Identify each adjoining edge unambiguously.
3. Ask for specific feature continuation: cloud ridge height, tangent, thickness,
   curvature, dark gaps and softness; or masonry/paper/roof features as appropriate.
   Keep the accepted palette and broad lighting. Generic “seamless sky” is too weak.
4. Reassemble with the exact original. Inspect that assembled output before
   accepting it. If a join fails, supply a contextual crop of THAT composite for
   a focused bridge edit, with unchanged scenery beyond both ends of the band.
5. Use a strict allowed-region composite. A textual preservation instruction is
   not a mask. Reject registration drift instead of silently resizing a repair.
   Restore the protected original, padding and alpha deterministically.
6. If structures now align but small edge differences remain, a one-sided
   boundary correction may help. In the private skyline experiment, a harmonic
   correction matched fixed surrounding pixels while retaining the AI bridge's
   gradients. It can alter local shading and is not a general approved processor.
   Do not use broad blur or forced edge-color equality as evidence of a good join.
7. Review the inner AND outer band edges, with the original bounds hidden, at
   native and fit/coarse scales. Trace individual features across the join and
   check value/gradient continuity separately. Look for moved seams, halos, flat
   strips, cut clouds and duplicated patterns. A tiny measured edge jump is not
   proof of structural continuity, especially when the processor enforces it.
8. Check 4:3, 16:10, 16:9, 21:9 and 32:9 from one shared master. Require exact
   original-center/alpha/padding checks and visual art review. Game integration
   still needs layer geometry, UV/scissor/loading support and real captures.

Retain raw model outputs and previous versions. Save exact prompts, input/output
hashes, guide/mask coordinates, transforms, processor code and checks with the
private experiment. No artwork belongs in the source repository. Nothing in this
workflow automatically approves, selects, exports or installs a candidate.

The first right-side repair missed lower cloud bands because both the allowed
region and the review crop ended too high. Expand the region through the whole
visible sky and horizon haze; review upper/middle/lower joins separately and use
a full-height crop. A successful opposite-side repair stays exact. Do not infer
whole-join acceptance from an upper-sky metric or cropped before/after alone.

For the second batch, a rigid roof silhouette required technical alpha/geometry
registration to the source edge's measured slope; color blending alone left a
step. Keep AI texture proposals but verify straight architectural planes and
their source coordinates. Generated-side alpha remains subject to art review.
A1024square bridge target returned1254square; assembly uniformly restored the
original1440square crop. The50%join and24%poster-top landmark stayed registered. Uniform full-canvas resolution normalization is
allowed only when aspect and landmark registration agree, with actual sizes and
transforms recorded. Reject crop, zoom, perspective or registration drift; never
silently stretch a repair in one axis. Restore protected pixels afterward.
