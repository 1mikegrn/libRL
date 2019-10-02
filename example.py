import libRL

def main():
    file_location = r'D:\Research and Teaching\University of Missouri-Kansas City\Dr. Xiaobo Chen\Microwave Absorption\Data\(nBu4)2Mo6 {A}'
    file_name = r'\data1'

    # res = libRL.RL(
    #     Mcalc=file_location + file_name + '.csv',
    #     f_set=(1,10,0.1), d_set=(0,5,1), interp='linear',
    #     multiprocessing=0, multicolumn=True
    # )

    res = libRL.CARL(
        Mcalc=file_location + file_name + '.csv',
        f_set=(1,10,0.1), as_dataframe=True
    )

    res.to_clipboard()

    print(res)

if __name__ == "__main__":
    main()
