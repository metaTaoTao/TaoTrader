import argparse

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--mode', choices=['backtest', 'live'], default='backtest')
    args = parser.parse_args()

    if args.mode == 'backtest':
        from run.run_backtest import run
    else:
        from run.run_live import run

    run()
