FUNCTION Main()
	CALL Print("MySum0(1, 10) = ", MySum0(1, 10), LF)
	CALL Print("MySum1(1, 10) = ", MySum1(1, 10), LF)
END

FUNCTION MySum0(Start, End)
	IF Start = End THEN
		RETURN End
	ELSE
		RETURN Start + MySum0(Start + 1, End)
	END
END

FUNCTION MySum1(Start, End)
	LET Result = 0
	DO
		IF Start = End THEN
			LET Result = Result + End
			EXIT
		ELSE
			LET Result = Result + Start
			LET Start = Start + 1
		END
	LOOP
	RETURN Result
END
