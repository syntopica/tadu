// Top offset of every row, plus the total height as the last entry.
export function rowOffsets(rows, groupHeight, cardHeight) {
  const offsets = new Array(rows.length + 1);
  offsets[0] = 0;
  for (let index = 0; index < rows.length; index += 1) {
    const height = rows[index].kind === "group" ? groupHeight : cardHeight;
    offsets[index + 1] = offsets[index] + height;
  }
  return offsets;
}
