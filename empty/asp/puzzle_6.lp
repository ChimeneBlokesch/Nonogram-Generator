#const c = 5. #const r = 5.
col_id(1..c). row_id(1..r).
cell(RowId, ColId) :- row_id(RowId), col_id(ColId).
{filled(RowId, ColId) : cell(RowId, ColId)}.
row_amount(1, 1, 1).
row_amount(2, 1, 3).
row_amount(2, 2, 1).
row_amount(3, 1, 1).
row_amount(3, 2, 1).
row_amount(4, 1, 1).
row_amount(4, 2, 1).
row_amount(5, 1, 1).
row_amount(5, 2, 1).
row_amount(5, 3, 1).
col_amount(1, 1, 1).
col_amount(1, 2, 2).
col_amount(2, 1, 1).
col_amount(3, 1, 2).
col_amount(3, 2, 1).
col_amount(4, 1, 1).
col_amount(4, 2, 1).
col_amount(5, 1, 2).
col_amount(5, 2, 1).

sequence_row(R, 1, C, C) :- row_id(R), col_id(C), filled(R, C).
sequence_row(R, 2, C1, C1+1) :- row_id(R), col_id(C1), filled(R, C1), filled(R, C1+1).
sequence_row(R, L, C1, C2) :- row_id(R), col_id(C1), col_id(C2), C1 < C2, filled(R, C1), filled(R, C2), sequence_row(R, L - 1, C1, C2-1).

sequence_col(C, 1, R, R) :- col_id(C), row_id(R), filled(R, C).
sequence_col(C, 2, R1, R1+1) :- col_id(C), row_id(R1), filled(R1, C), filled(R1+1, C).
sequence_col(C, L, R1, R2) :- col_id(C), row_id(R1), row_id(R2), R1 < R2, filled(R1, C), filled(R2, C), sequence_col(C, L - 1, R1, R2-1).

group_row(R, 1, L, C1, C2) :- row_id(R), sequence_row(R, L, C1, C2),
                                not filled(R, C1-1), not filled(R, C2+1),
                                not sequence_row(R, _, C3, _) : col_id(C3), C3 < C1.

group_row(R, I, L, C3, C4) :- row_id(R), sequence_row(R, L, C3, C4), I > 1, col_id(C3), col_id(C4), % existence of group
                                not filled(R, C3-1), not filled(R, C4+1), % seperated group
                                group_row(R, I-1, _, _, C2), col_id(C2), C3 > C2, % previous group has a lower id
                                not group_row(R, I, _, C, _) : col_id(C), C3 != C. % no other group with the same id

group_col(C, 1, L, R1, R2) :- col_id(C), sequence_col(C, L, R1, R2),
                                not filled(R1-1, C), not filled(R2+1, C),
                                not sequence_col(C, _, R3, _) : row_id(R3), R3 < R1.

group_col(C, I, L, R3, R4) :- col_id(C), sequence_col(C, L, R3, R4), I > 1, row_id(R3), row_id(R4), % existence of group
                                not filled(R3-1, C), not filled(R4+1, C), % seperated group
                                group_col(C, I-1, _, _, R2), row_id(R2), R3 > R2, % previous group has a lower id
                                not group_col(C, I, _, R, _) : row_id(R), R3 != R. % no other group with the same id


% All rows and columns have the correct amount of filled cells
:- not group_row(R, I, L, _, _), row_amount(R, I, L).
:- not group_col(C, I, L, _, _), col_amount(C, I, L).

:- group_row(R, I, L, _, _), not row_amount(R, I, L).
:- group_col(C, I, L, _, _), not col_amount(C, I, L).

#show filled/2.

