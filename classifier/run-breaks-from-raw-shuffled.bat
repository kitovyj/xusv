SET EPOCHS0=30
SET EPOCHS1=20
SET SR=100
SET OUTDIR=cv_breaks_shuffled

MKDIR train
MKDIR train\%OUTDIR%

FOR /L %%C IN (0,1,9) DO (

    MKDIR train\%OUTDIR%\%%C

    python -u ./train-gender-from-raw.py --epochs %EPOCHS0% --kernel-sizes 10 5 3 3 --features 256 256 256 256 --max-pooling 1 1 1 1 --strides 2 2 1 1 --fc-num 2 --fc-sizes 15 15 --dropout 0.0 --regularization 0.0000 --learning-rate 0.001 --batch-normalization --summary-records %SR% --test-chunk %%C --shuffled --data-path ./raw-data-breaks
    REN train\*.tfevents* pretrained.tfevents
    MOVE train\pretrained.tfevents train\%OUTDIR%\%%C\

    python -u ./train-gender-from-raw.py --epochs %EPOCHS1% --kernel-sizes 10 5 3 3 --features 256 256 256 256 --max-pooling 1 1 1 1 --strides 2 2 1 1 --fc-num 2 --fc-sizes 15 15 --dropout 0.5 --regularization 0.0000 --learning-rate 0.0001 --batch-normalization --summary-records %SR% --test-chunk %%C --summary-file train\%OUTDIR%\%%C\pretrained.tfevents --shuffled --data-path ./raw-data-breaks
    REN train\*.tfevents* pretrained-1.tfevents
    MOVE train\pretrained-1.tfevents train\%OUTDIR%\%%C\

)