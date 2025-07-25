from copy import copy


def merge_and_style(
    ws,
    row,
    col_from,
    col_to,
    value=None,
    font=None,
    fill=None,
    align=None,
    border=None,
):
    ws.merge_cells(start_row=row, start_column=col_from, end_row=row, end_column=col_to)
    cell = ws.cell(row, col_from, value)
    if font:
        cell.font = copy(font)
    if fill:
        cell.fill = copy(fill)
    if align:
        cell.alignment = copy(align)
    if border:
        for col in range(col_from, col_to + 1):
            ws.cell(row, col).border = copy(border)
    return cell


def set_row_style(
    ws,
    row,
    font=None,
    fill=None,
    align=None,
    border=None,
    col_from=1,
    col_to=12,
):
    from copy import copy

    for col in range(col_from, col_to + 1):
        cell = ws.cell(row, col)
        if font:
            cell.font = copy(font)
        if fill:
            cell.fill = copy(fill)
        if align:
            cell.alignment = copy(align)
        if border:
            cell.border = copy(border)
