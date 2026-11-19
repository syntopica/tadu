// What tadu said, for the page: the command line's hints on how to write
// ("add --write", "run again with --write") are left out, since Apply is
// the page's way to write.
export function previewText(output) {
  return output.replace(/ \(dry run: add --write\)|; run again with --write|^\(dry run: add --write\)\n?/gm, "");
}
