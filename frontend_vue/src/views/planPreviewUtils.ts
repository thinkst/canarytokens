// Utils just to serve the static Plan Preview
// Remove this file when the Plan will be merged
import { ref } from 'vue';
import type { ProposedAWSInfraTokenPlanData } from '@/components/tokens/aws_infra/types.ts';

export function generateDataChoice() {
  return new Promise((resolve) => {
    setTimeout(() => {
      resolve({
        result: 'true',
        message: '',
        proposed_data: 'Lorem ipsum data',
      });
    }, 200);
  });
}

export const assetsExample = ref<ProposedAWSInfraTokenPlanData>({
  S3Bucket: [
    {
      bucket_name: 'stagingcustomersab5rcqvgz',
      objects: [
        {
          object_path: '2016/9y6MmQsbxg/object',
        },
        {
          object_path: '2012/4guCu7i4kU/object',
        },
        {
          object_path: '2017/tIJXkV2zU9/text',
        },
        {
          object_path: '2022/w1hWemKszJ/passwords',
        },
        {
          object_path: '2016/YqkZZMKvCr/passwords',
        },
        {
          object_path: '2003/9hfbHNqxlC/object',
        },
        {
          object_path: '2005/kTwM5c8lx2/text',
        },
        {
          object_path: '2011/OJVkCTiYNi/passwords',
        },
        {
          object_path: '2009/uXTk29uqsj/object',
        },
        {
          object_path: '2004/XLjRDbnTdQ/object',
        },
        {
          object_path: '2005/6QgmMfrhTg/passwords',
        },
        {
          object_path: '2014/sZRd7XM6PP/data',
        },
        {
          object_path: '2016/YjTSGWepfy/text',
        },
        {
          object_path: '2025/xhBYSpjPAV/passwords',
        },
        {
          object_path: '2001/nr0Edh7dQl/data',
        },
        {
          object_path: '2010/W1icZkS0OT/data',
        },
        {
          object_path: '2023/EJhGkRAgFv/text',
        },
        {
          object_path: '2022/tn895QcVLj/passwords',
        },
        {
          object_path: '2008/IZCrFDN6kG/data',
        },
        {
          object_path: '2012/kUv9Ehw37Q/passwords',
        },
        {
          object_path: '2013/RQyAS9zeoS/data',
        },
        {
          object_path: '2020/YU3i9Iu1HN/data',
        },
        {
          object_path: '2022/JS2gwoPujj/object',
        },
        {
          object_path: '2007/EnBveP5AFa/data',
        },
        {
          object_path: '2005/ZGiyyorje0/data',
        },
        {
          object_path: '2009/YGuvE5RRTA/data',
        },
        {
          object_path: '2003/DqsG2jzJFj/data',
        },
        {
          object_path: '2006/QMoVCuMStr/passwords',
        },
        {
          object_path: '2004/gYOfMNJxJk/text',
        },
        {
          object_path: '2004/GunT2jyMiV/passwords',
        },
        {
          object_path: '2004/H67vC0whFx/object',
        },
        {
          object_path: '2002/UwiCJe06XX/text',
        },
        {
          object_path: '2016/ZgaVv6dIdw/text',
        },
        {
          object_path: '2016/adf7FMk05j/data',
        },
        {
          object_path: '2018/hmDqgqWf5S/object',
        },
        {
          object_path: '2018/4iSdEKEvXc/text',
        },
        {
          object_path: '2015/QdmswqFYI0/object',
        },
        {
          object_path: '2019/M8YofqbETv/passwords',
        },
        {
          object_path: '2021/LiRdw8Ahb5/data',
        },
        {
          object_path: '2024/cDzCawt0aJ/passwords',
        },
        {
          object_path: '2001/l8k6MUUxpD/data',
        },
        {
          object_path: '2018/nbYktHECji/text',
        },
        {
          object_path: '2013/wx8VyjuM8U/object',
        },
        {
          object_path: '2011/Pw93HVUKfx/object',
        },
        {
          object_path: '2006/7wUUpNuTDs/text',
        },
        {
          object_path: '2004/yB7TXeqOga/object',
        },
        {
          object_path: '2025/ZuSs8HbgVe/text',
        },
        {
          object_path: '2003/mlkZmcCM0E/data',
        },
      ],
      off_inventory: false,
    },
    {
      bucket_name: 'testinguseryq78uglinf',
      objects: [
        {
          object_path: '2004/Ga1qxxIb2K/object',
        },
        {
          object_path: '2024/PtiUBKQiY4/text',
        },
        {
          object_path: '2020/DxF8qGADjy/text',
        },
        {
          object_path: '2015/8sTsb9S5JE/text',
        },
        {
          object_path: '2023/vo6GVOJV1f/text',
        },
        {
          object_path: '2023/FVBbe85u6e/object',
        },
        {
          object_path: '2013/mOXjUBOJnQ/passwords',
        },
        {
          object_path: '2003/nNU7kkN9UM/passwords',
        },
        {
          object_path: '2011/2rCYohmuP1/object',
        },
        {
          object_path: '2004/GOfGpowQpi/object',
        },
        {
          object_path: '2000/x1JRAyhAOv/data',
        },
        {
          object_path: '2024/KMtFCflhGP/passwords',
        },
        {
          object_path: '2002/sW5PTjpuAo/passwords',
        },
        {
          object_path: '2007/CTnqyVLgMU/passwords',
        },
        {
          object_path: '2025/eppPTnUWTQ/object',
        },
        {
          object_path: '2008/IGRvH1TVp3/data',
        },
        {
          object_path: '2021/fWqSzN1unW/text',
        },
        {
          object_path: '2019/rIZkYOZEV1/object',
        },
        {
          object_path: '2012/MNJOitHHbg/passwords',
        },
        {
          object_path: '2017/eVZR00Vyi7/data',
        },
        {
          object_path: '2010/eJU6VllV5l/passwords',
        },
        {
          object_path: '2016/4oJEyhCQUc/object',
        },
        {
          object_path: '2005/HczgGQYodd/text',
        },
        {
          object_path: '2001/3pswopT7n5/object',
        },
        {
          object_path: '2006/oFFovnZxll/data',
        },
        {
          object_path: '2023/xYveYM66Ox/data',
        },
        {
          object_path: '2013/fggr0dnN9q/text',
        },
        {
          object_path: '2002/WHlQD68rob/data',
        },
        {
          object_path: '2017/jPkii6fAV8/object',
        },
        {
          object_path: '2003/MuaqFVRjj4/data',
        },
        {
          object_path: '2000/RBcuNmhYF8/text',
        },
        {
          object_path: '2012/8Sp9FBiv09/data',
        },
        {
          object_path: '2015/m3UTQSx7EO/text',
        },
        {
          object_path: '2003/RthD2MF2Yn/text',
        },
        {
          object_path: '2005/R3EPOh1BVY/passwords',
        },
        {
          object_path: '2013/cZ3aIXuUdP/data',
        },
      ],
      off_inventory: false,
    },
    {
      bucket_name: 'stagingaudite9cmwsae5q',
      objects: [
        {
          object_path: '2024/1yWC66Ls0x/object',
        },
        {
          object_path: '2003/LhsLck5b0u/text',
        },
        {
          object_path: '2021/rGuUZqd3lz/passwords',
        },
        {
          object_path: '2006/b89xmL0UPz/object',
        },
        {
          object_path: '2014/LaF8syCFfA/passwords',
        },
        {
          object_path: '2014/kPRbOe5x1k/passwords',
        },
        {
          object_path: '2023/0wlpo8YoDg/passwords',
        },
        {
          object_path: '2023/VjUSgBBwwO/text',
        },
        {
          object_path: '2003/pOsXWK8LUh/passwords',
        },
        {
          object_path: '2002/yf0vKdl3I2/text',
        },
        {
          object_path: '2005/MHkMhdCmNT/text',
        },
        {
          object_path: '2000/C25FIL56D9/passwords',
        },
        {
          object_path: '2016/ojvD2ElrMl/data',
        },
        {
          object_path: '2006/ew51NnUENd/passwords',
        },
        {
          object_path: '2002/qVh3iOYpxR/passwords',
        },
        {
          object_path: '2023/5X2w1AByUJ/text',
        },
        {
          object_path: '2013/UlvTcQejM4/object',
        },
        {
          object_path: '2001/T4M1T9aCwU/data',
        },
        {
          object_path: '2024/aBy6LAQYkf/object',
        },
        {
          object_path: '2008/TaWpxdTkwz/passwords',
        },
        {
          object_path: '2006/DsppvjpGmS/passwords',
        },
        {
          object_path: '2014/4wDjv0SDHE/data',
        },
        {
          object_path: '2019/YcjioPqgsI/object',
        },
        {
          object_path: '2007/Ld7hHUlQ5f/passwords',
        },
        {
          object_path: '2007/bacPsdzgtH/data',
        },
        {
          object_path: '2010/v1HLrikDoK/text',
        },
        {
          object_path: '2016/4GN5O05coV/passwords',
        },
        {
          object_path: '2015/oqsh1a0pdV/passwords',
        },
        {
          object_path: '2006/h66Mh47eNW/data',
        },
        {
          object_path: '2018/ehu436Yj5Z/data',
        },
        {
          object_path: '2009/CwAPi0gpiY/data',
        },
        {
          object_path: '2011/PWfANK64ll/object',
        },
        {
          object_path: '2006/yzG6JcSyNU/data',
        },
        {
          object_path: '2011/XCMWpYLfZm/passwords',
        },
        {
          object_path: '2005/r6OX0s73hv/passwords',
        },
        {
          object_path: '2008/3x4azK0eid/passwords',
        },
        {
          object_path: '2020/n6szSghacx/text',
        },
        {
          object_path: '2008/dhzgmkjWuM/text',
        },
        {
          object_path: '2023/xdHIAyVaRO/object',
        },
        {
          object_path: '2017/2ZQLgYmNlm/data',
        },
        {
          object_path: '2024/6ZlIabBdVd/passwords',
        },
        {
          object_path: '2018/wq1l6epnWC/text',
        },
        {
          object_path: '2011/4vxdIh3iCb/data',
        },
        {
          object_path: '2012/qGUuXXIWoP/text',
        },
        {
          object_path: '2016/MHVqBIc9s0/data',
        },
        {
          object_path: '2014/S5SDwFbmeP/object',
        },
        {
          object_path: '2012/KttkSHThxk/text',
        },
        {
          object_path: '2006/NYQwrVNgZ0/passwords',
        },
        {
          object_path: '2023/9qR0jvJd3Y/object',
        },
        {
          object_path: '2023/kcdAwU422v/data',
        },
        {
          object_path: '2008/O9qSIb8KeD/data',
        },
        {
          object_path: '2003/KoWZfVIq3i/passwords',
        },
        {
          object_path: '2017/z4pzdvXQAS/passwords',
        },
        {
          object_path: '2020/ZYk0AvGe4Q/object',
        },
        {
          object_path: '2012/p97Q7bDm0S/passwords',
        },
        {
          object_path: '2025/qZ3FNvcPPH/text',
        },
        {
          object_path: '2009/S608Db7vHk/object',
        },
        {
          object_path: '2022/zo950QCqqF/data',
        },
        {
          object_path: '2002/8MJ8rhIz1o/passwords',
        },
        {
          object_path: '2004/YChiihjsi8/text',
        },
        {
          object_path: '2005/cB8LiZDK5E/object',
        },
        {
          object_path: '2019/UqFGHfrk59/data',
        },
        {
          object_path: '2007/l7fUjc2s3F/passwords',
        },
        {
          object_path: '2004/0jyXyPVM9Q/object',
        },
        {
          object_path: '2006/j9YMKTt4Su/data',
        },
        {
          object_path: '2015/B0mjqOy9WC/data',
        },
        {
          object_path: '2004/PdEofgHGOF/data',
        },
      ],
      off_inventory: false,
    },
    {
      bucket_name: 'staging-user-88s10ql3g9',
      objects: [
        {
          object_path: '2005/pvUC7gbMy7/object',
        },
        {
          object_path: '2014/7mvaxRgV2c/object',
        },
        {
          object_path: '2022/f6gwzNyGKz/data',
        },
        {
          object_path: '2024/uXUuHh8zfy/passwords',
        },
        {
          object_path: '2004/P1YsHokYdw/data',
        },
        {
          object_path: '2015/mHDACqltMs/passwords',
        },
        {
          object_path: '2020/7P7WIb7juy/text',
        },
        {
          object_path: '2015/Mmo0kEjLKA/passwords',
        },
        {
          object_path: '2007/AbYcrUUSPx/text',
        },
        {
          object_path: '2020/L9xZQ3P64k/passwords',
        },
        {
          object_path: '2015/qh0aczSWDW/text',
        },
        {
          object_path: '2008/PeNBJdcv2K/object',
        },
        {
          object_path: '2014/8sYIiK6UBf/object',
        },
        {
          object_path: '2012/Nl2ePeKDy8/data',
        },
        {
          object_path: '2019/bCQTK3DjtD/passwords',
        },
        {
          object_path: '2022/XJqyP1eraU/passwords',
        },
        {
          object_path: '2007/uODReaq8vb/passwords',
        },
        {
          object_path: '2002/jaoXmVJttY/passwords',
        },
        {
          object_path: '2012/u2fQWijtTs/object',
        },
        {
          object_path: '2013/M1B9wce0Nk/text',
        },
        {
          object_path: '2011/CNztmUmvFT/text',
        },
        {
          object_path: '2004/kjTyknKar5/passwords',
        },
        {
          object_path: '2011/KezQJ1mYHF/text',
        },
        {
          object_path: '2021/IhoA3e2A4A/object',
        },
        {
          object_path: '2008/H9Z4jHTMFG/data',
        },
        {
          object_path: '2011/xQZy2Xexwk/text',
        },
      ],
      off_inventory: false,
    },
    {
      bucket_name: 'staging-customer-bjcg4qempq',
      objects: [
        {
          object_path: '2025/ZpzsaQErDF/object',
        },
        {
          object_path: '2025/Dns50gcfZ8/text',
        },
        {
          object_path: '2000/btc3wVzX9W/passwords',
        },
        {
          object_path: '2002/Alk2W3qRgZ/object',
        },
        {
          object_path: '2021/CkAKdpLS9M/text',
        },
        {
          object_path: '2006/YYGcMrTW4v/data',
        },
        {
          object_path: '2006/WQjmAcGy2w/data',
        },
        {
          object_path: '2012/HWloLPHirk/data',
        },
        {
          object_path: '2015/ra60MRphT7/passwords',
        },
        {
          object_path: '2000/NM6VSgKFnd/passwords',
        },
        {
          object_path: '2005/YkO0JhjaWI/text',
        },
        {
          object_path: '2014/ONnO2u4clg/object',
        },
        {
          object_path: '2014/uU0cL6UFMn/object',
        },
        {
          object_path: '2007/qMvwmIpl4k/passwords',
        },
        {
          object_path: '2010/BES5GcQ2ZN/text',
        },
        {
          object_path: '2015/M9FjQ5Fzj1/text',
        },
        {
          object_path: '2008/nh6z2VdPa8/data',
        },
        {
          object_path: '2013/iLzS4RSDQK/data',
        },
        {
          object_path: '2018/eAD24VrGcb/text',
        },
        {
          object_path: '2023/HkP7skV2Mg/object',
        },
        {
          object_path: '2020/T7QlASf0yN/data',
        },
        {
          object_path: '2019/ZjjhLNhYwf/text',
        },
        {
          object_path: '2006/WSkg7QhQUg/object',
        },
        {
          object_path: '2015/8uqcFaXlZd/data',
        },
        {
          object_path: '2019/V75mXI8rpl/text',
        },
        {
          object_path: '2010/07LVJqCZUA/object',
        },
        {
          object_path: '2002/hMG4eq4CMc/object',
        },
        {
          object_path: '2011/VMTG055e7r/object',
        },
        {
          object_path: '2014/QZg4Jv2YXr/text',
        },
        {
          object_path: '2014/h9iXANpSaz/object',
        },
        {
          object_path: '2001/mK5362NCYu/object',
        },
        {
          object_path: '2022/c2bWF2KOiM/object',
        },
        {
          object_path: '2012/JzeZapCBDc/passwords',
        },
        {
          object_path: '2007/HxDbEdLnmo/passwords',
        },
        {
          object_path: '2015/UKomMXImHI/passwords',
        },
        {
          object_path: '2013/4zNh3198qc/object',
        },
        {
          object_path: '2002/0ORgaiR1bR/text',
        },
        {
          object_path: '2009/9GNd8PfLZX/object',
        },
        {
          object_path: '2002/yNvPerncxN/data',
        },
        {
          object_path: '2002/mHEGhP7XCg/text',
        },
        {
          object_path: '2023/fFtrAhvwuu/text',
        },
        {
          object_path: '2020/6asj4l4c5m/data',
        },
        {
          object_path: '2000/C9qqduKkVu/data',
        },
        {
          object_path: '2024/UOSDz7SA2O/passwords',
        },
        {
          object_path: '2021/bVkIsjuOKw/text',
        },
        {
          object_path: '2001/HFR0jc8w4N/object',
        },
        {
          object_path: '2012/flXnjVjuDx/passwords',
        },
        {
          object_path: '2022/viztYBXYqy/data',
        },
        {
          object_path: '2012/xByDzsu0ej/passwords',
        },
        {
          object_path: '2011/EtXUKmmT7N/passwords',
        },
        {
          object_path: '2003/kOAhRrvMl6/object',
        },
        {
          object_path: '2011/CGHewWysnY/object',
        },
        {
          object_path: '2017/xRFJE9DRVM/object',
        },
        {
          object_path: '2004/O00CaMyfSt/data',
        },
        {
          object_path: '2019/Os27oIDztT/object',
        },
        {
          object_path: '2001/tolnAjm04s/data',
        },
        {
          object_path: '2009/AtA3cube0F/object',
        },
        {
          object_path: '2007/nQ8TjdMiGG/object',
        },
        {
          object_path: '2019/lOHwZD73HP/data',
        },
        {
          object_path: '2002/xqiW5k5Efv/data',
        },
        {
          object_path: '2013/v0Q9E6KLGq/text',
        },
        {
          object_path: '2007/RLqnMNiekf/text',
        },
        {
          object_path: '2014/W2i54tknR3/text',
        },
        {
          object_path: '2010/9efD18mw5b/object',
        },
        {
          object_path: '2004/9tvJyXj8WL/passwords',
        },
        {
          object_path: '2006/fU3qg0D8Hu/passwords',
        },
        {
          object_path: '2005/o2w1s4aAJr/passwords',
        },
        {
          object_path: '2004/cDcUpwlzWV/text',
        },
        {
          object_path: '2008/k7wsKlccwp/object',
        },
        {
          object_path: '2016/WJY4nemZQf/data',
        },
        {
          object_path: '2001/6cSVbqFgxb/passwords',
        },
        {
          object_path: '2013/rX1DVmC86O/passwords',
        },
        {
          object_path: '2021/c4F4nwX18w/text',
        },
        {
          object_path: '2022/i7UBz42xGe/object',
        },
        {
          object_path: '2012/cKPgfhFidX/passwords',
        },
        {
          object_path: '2004/q7TAkGjQpT/object',
        },
        {
          object_path: '2014/f5oCWb1VzL/passwords',
        },
        {
          object_path: '2018/2KyW3bWGz2/data',
        },
        {
          object_path: '2019/4uT7hVVGvs/text',
        },
        {
          object_path: '2020/lMOaIkHsPt/passwords',
        },
        {
          object_path: '2006/RSbWfMaJQ0/text',
        },
        {
          object_path: '2007/fCAVXqWhdB/text',
        },
        {
          object_path: '2015/DwN1CLa20S/text',
        },
        {
          object_path: '2009/QSdyTEIm06/passwords',
        },
        {
          object_path: '2021/QmQOXriv55/object',
        },
        {
          object_path: '2018/5Tb8GDjx0w/text',
        },
      ],
      off_inventory: false,
    },
    {
      bucket_name: 'devcustomergtkbml1db1',
      objects: [
        {
          object_path: '2018/jcbAdbspyI/object',
        },
        {
          object_path: '2017/v9cvvdRCSI/data',
        },
        {
          object_path: '2000/fU7nIEoZd3/passwords',
        },
        {
          object_path: '2000/sM86uiBqCy/passwords',
        },
        {
          object_path: '2023/ub2gUIfUAL/text',
        },
        {
          object_path: '2019/xIT8S72jdy/passwords',
        },
        {
          object_path: '2006/4gqgDtdj6V/data',
        },
        {
          object_path: '2025/QDK2mPfZwr/passwords',
        },
        {
          object_path: '2014/tdsPSWqzqu/object',
        },
        {
          object_path: '2013/3JIGJXoTCM/text',
        },
        {
          object_path: '2019/tI0NrdM5Gn/text',
        },
        {
          object_path: '2013/iBjJqT8PhC/text',
        },
        {
          object_path: '2000/Qe4eZeTxxS/text',
        },
        {
          object_path: '2016/DfFTOcQGpS/object',
        },
        {
          object_path: '2019/NChGveLBCa/data',
        },
        {
          object_path: '2001/cnwNkMCJvu/passwords',
        },
        {
          object_path: '2019/GSiUv7NpLv/data',
        },
        {
          object_path: '2002/h27uocdf0Q/data',
        },
        {
          object_path: '2002/KwPKrZogTh/passwords',
        },
        {
          object_path: '2016/1kY6JBwIE7/data',
        },
        {
          object_path: '2011/H1R5AcpwYx/passwords',
        },
        {
          object_path: '2019/66wLuivRse/data',
        },
        {
          object_path: '2004/9iVjPml15t/data',
        },
        {
          object_path: '2008/SxcMtjZK7y/object',
        },
        {
          object_path: '2006/XH8SSAadAO/object',
        },
        {
          object_path: '2009/SP5RgFVDPt/object',
        },
        {
          object_path: '2005/40HHeuClLA/passwords',
        },
        {
          object_path: '2015/pajMZjhFAD/passwords',
        },
        {
          object_path: '2007/jQXN6JbbJM/data',
        },
        {
          object_path: '2019/chSJFpV1wP/passwords',
        },
        {
          object_path: '2007/k7k1XnKg2j/object',
        },
        {
          object_path: '2003/bapudrmLyW/passwords',
        },
        {
          object_path: '2002/00YSnGb3rA/text',
        },
        {
          object_path: '2025/5Lo6pemFP0/object',
        },
        {
          object_path: '2000/Ev1d7fOoDh/object',
        },
        {
          object_path: '2006/3o4xccF2s2/data',
        },
        {
          object_path: '2014/FiYPVlQRm0/text',
        },
        {
          object_path: '2001/xodPBUsvMH/data',
        },
        {
          object_path: '2016/sdfaYfqFnL/passwords',
        },
        {
          object_path: '2015/9SwhKZLQex/data',
        },
        {
          object_path: '2010/8BM0RANaWw/text',
        },
        {
          object_path: '2024/o9e5dYeufI/text',
        },
        {
          object_path: '2017/9WTIg7GnZW/passwords',
        },
        {
          object_path: '2010/1cjckUaAhV/text',
        },
        {
          object_path: '2011/kCogXUaiIp/passwords',
        },
        {
          object_path: '2009/WX511tKTqF/passwords',
        },
        {
          object_path: '2019/WwAofHDjJb/text',
        },
        {
          object_path: '2025/piQNhM5Nrs/data',
        },
        {
          object_path: '2025/CqRC7eTSol/passwords',
        },
        {
          object_path: '2013/TJwswzzmF5/passwords',
        },
        {
          object_path: '2021/cRy01UlSFm/text',
        },
        {
          object_path: '2014/bd5cayfkH9/text',
        },
        {
          object_path: '2011/fhPLa5uIMJ/data',
        },
        {
          object_path: '2024/1fp3cctP1F/object',
        },
        {
          object_path: '2019/ckkihskg9p/passwords',
        },
        {
          object_path: '2015/0ibQiPw5O9/passwords',
        },
        {
          object_path: '2003/LBX2mpQJn4/passwords',
        },
      ],
      off_inventory: false,
    },
    {
      bucket_name: 'devadminmgs7fk30k9',
      objects: [
        {
          object_path: '2020/ofuL799OC6/passwords',
        },
        {
          object_path: '2002/CldtinEfm5/data',
        },
        {
          object_path: '2003/QQNiQegelz/passwords',
        },
        {
          object_path: '2003/t90MAB5mDs/text',
        },
        {
          object_path: '2010/fmXpHFxA4n/data',
        },
        {
          object_path: '2024/qxpBTLUswK/data',
        },
        {
          object_path: '2023/LLheIftrDM/text',
        },
        {
          object_path: '2015/9dHQa4doBT/data',
        },
        {
          object_path: '2009/rBBCjTdacr/passwords',
        },
        {
          object_path: '2004/1KTsouIIBt/data',
        },
        {
          object_path: '2019/ylgYfhiCUK/data',
        },
        {
          object_path: '2017/xqOTohnx6g/text',
        },
        {
          object_path: '2015/ateHVNruxY/data',
        },
        {
          object_path: '2009/uOKvVE1Nuk/text',
        },
        {
          object_path: '2011/NAqGexezm5/passwords',
        },
        {
          object_path: '2015/nVxcfDDuhy/data',
        },
        {
          object_path: '2011/xcZsxwttOH/data',
        },
        {
          object_path: '2016/m6nSY5HDhi/object',
        },
        {
          object_path: '2024/vLl34CWjDj/object',
        },
        {
          object_path: '2016/6UK1l3Y0zX/data',
        },
        {
          object_path: '2008/qghDbBfdLB/data',
        },
        {
          object_path: '2010/IXTJgb8o2u/passwords',
        },
        {
          object_path: '2002/ihlONDO2Qr/text',
        },
        {
          object_path: '2002/OqHkeFpOUs/data',
        },
        {
          object_path: '2004/mU1kN2ggsu/object',
        },
        {
          object_path: '2003/yiibYF4A3q/passwords',
        },
        {
          object_path: '2008/RjrNClRRMo/passwords',
        },
        {
          object_path: '2021/hWB3r0KzmJ/data',
        },
        {
          object_path: '2023/Kv5iWLog4d/object',
        },
        {
          object_path: '2021/phweciEymK/object',
        },
        {
          object_path: '2008/n8FEqrLA1i/text',
        },
        {
          object_path: '2002/Cub8vdJi74/object',
        },
        {
          object_path: '2019/FOv8bokhXm/object',
        },
        {
          object_path: '2021/EdQk3MBBms/text',
        },
        {
          object_path: '2001/HkTdaK1Elz/object',
        },
        {
          object_path: '2008/1kfVbeHYYP/object',
        },
        {
          object_path: '2018/rQwXTojKpX/data',
        },
        {
          object_path: '2011/zYOO9UfjMv/object',
        },
        {
          object_path: '2015/eEwEDgBmlo/object',
        },
        {
          object_path: '2005/ICAcHUZtd8/passwords',
        },
        {
          object_path: '2021/EHSO8tvAtO/object',
        },
        {
          object_path: '2007/GpiKPCT1rs/passwords',
        },
        {
          object_path: '2006/1fGuI2TzJ4/object',
        },
        {
          object_path: '2012/rKDp66G6Zb/data',
        },
        {
          object_path: '2002/WIt9S1WkGV/data',
        },
        {
          object_path: '2020/QpL4smps05/data',
        },
        {
          object_path: '2024/2bVLX8PAxP/text',
        },
        {
          object_path: '2002/C2ngVrXFK9/passwords',
        },
        {
          object_path: '2011/C1gnkWH3H8/data',
        },
      ],
      off_inventory: false,
    },
    {
      bucket_name: 'dev-audit-qa6lrh6f53',
      objects: [
        {
          object_path: '2001/IwWeUYSeEf/data',
        },
        {
          object_path: '2012/OMH6BSFc2k/passwords',
        },
        {
          object_path: '2016/7kSfudpKPK/passwords',
        },
        {
          object_path: '2003/Z9FBIqPIMG/text',
        },
        {
          object_path: '2010/DE9w9Ze0h7/object',
        },
        {
          object_path: '2017/LMbhJTtQpe/object',
        },
        {
          object_path: '2021/rRdFYDcFXP/object',
        },
        {
          object_path: '2000/RAWRAEOScL/data',
        },
        {
          object_path: '2025/F2Gqb62l0J/text',
        },
      ],
      off_inventory: false,
    },
  ],
  SQSQueue: [
    {
      sqs_queue_name: 'testing_admin_',
      off_inventory: false,
    },
    {
      sqs_queue_name: 'prod-admin-',
      off_inventory: false,
    },
    {
      sqs_queue_name: 'prod_audit_',
      off_inventory: false,
    },
    {
      sqs_queue_name: 'staginguser',
      off_inventory: false,
    },
    {
      sqs_queue_name: 'dev-audit-',
      off_inventory: false,
    },
    {
      sqs_queue_name: 'staging-audit-',
      off_inventory: false,
    },
    {
      sqs_queue_name: 'dev_user_',
      off_inventory: false,
    },
  ],
  SSMParameter: [
    {
      ssm_parameter_name: 'staging-admin-',
      off_inventory: false,
    },
    {
      ssm_parameter_name: 'devadmin',
      off_inventory: false,
    },
    {
      ssm_parameter_name: 'dev_user_',
      off_inventory: false,
    },
    {
      ssm_parameter_name: 'staging_customer_',
      off_inventory: false,
    },
    {
      ssm_parameter_name: 'devaudit',
      off_inventory: false,
    },
    {
      ssm_parameter_name: 'devuser',
      off_inventory: false,
    },
    {
      ssm_parameter_name: 'prod-customer-',
      off_inventory: false,
    },
    {
      ssm_parameter_name: 'prodadmin',
      off_inventory: false,
    },
    {
      ssm_parameter_name: 'prod_admin_',
      off_inventory: false,
    },
  ],
  SecretsManagerSecret: [
    {
      secret_name: 'testingadmin',
      off_inventory: false,
    },
    {
      secret_name: 'staginguser',
      off_inventory: false,
    },
    {
      secret_name: 'prod-customer-',
      off_inventory: false,
    },
    {
      secret_name: 'prod=customer=',
      off_inventory: false,
    },
    {
      secret_name: 'staging@admin@',
      off_inventory: false,
    },
    {
      secret_name: 'prodcustomer',
      off_inventory: false,
    },
    {
      secret_name: 'prod+admin+',
      off_inventory: false,
    },
  ],
  DynamoDBTable: [
    {
      table_name: 'testing_admin_',
      off_inventory: false,
      table_items: [
        'text_9d7w9',
        'object-9qx1l',
        'passwordskai75',
        'passwords_x0ejf',
        'objecty58h1',
        'passwords4jxw3',
        'object-g8isj',
        'data-kri38',
        'passwords-m6vkc',
        'data_d5urt',
        'dataki7xi',
        'textt71wp',
        'text_xvvi8',
        'object_d2xul',
        'object-48b3o',
        'text_wfhbg',
        'object1ig2x',
        'textb828r',
        'data_hqdf2',
        'passwords-g2iym',
        'passwords-tryuz',
        'object-xjct6',
        'data_gvj41',
        'passwords-xbbd0',
        'textt5l5k',
        'text_1m2xu',
        'passwords_6ejnl',
        'data_m0n33',
        'datamy5ix',
        'object-ztzhx',
        'text-0inho',
        'passwords2qspa',
        'text_qfnnr',
        'data5tuhm',
        'text_hsl4s',
        'text-env9w',
        'datag0b0z',
        'text_lbckr',
        'dataccwuq',
        'passwords_jxhfb',
        'data_8muf0',
        'passwordskbezg',
        'objecteflm9',
        'passwords-317iz',
        'data-b03qv',
        'data-jor2p',
        'passwords_362h1',
        'textf5y2j',
        'object_2a9rr',
        'passwords-kafe7',
        'text7ls9n',
        'passwords-lnzhs',
        'object2gx8l',
        'data_uwtuv',
        'text_51uvs',
        'datafj2cl',
        'data_rdlqc',
        'textd6akk',
        'text_daol6',
        'text_nuttr',
        'objectablo4',
        'data4zthj',
        'objectyd92u',
        'textltepg',
        'object8d4et',
        'passwordsuy025',
        'text_xn3ox',
        'data_8ro6x',
        'textnqfn6',
      ],
    },
  ],
});

export const assetsWithEmptySQSQueue = ref<ProposedAWSInfraTokenPlanData>({
  S3Bucket: [
    {
      bucket_name: 'stagingcustomersab5rcqvgz',
      objects: [
        {
          object_path: '2016/9y6MmQsbxg/object',
        },
        {
          object_path: '2012/4guCu7i4kU/object',
        },
        {
          object_path: '2017/tIJXkV2zU9/text',
        },
        {
          object_path: '2022/w1hWemKszJ/passwords',
        },
        {
          object_path: '2016/YqkZZMKvCr/passwords',
        },
        {
          object_path: '2003/9hfbHNqxlC/object',
        },
        {
          object_path: '2005/kTwM5c8lx2/text',
        },
        {
          object_path: '2011/OJVkCTiYNi/passwords',
        },
        {
          object_path: '2009/uXTk29uqsj/object',
        },
        {
          object_path: '2004/XLjRDbnTdQ/object',
        },
        {
          object_path: '2005/6QgmMfrhTg/passwords',
        },
        {
          object_path: '2014/sZRd7XM6PP/data',
        },
        {
          object_path: '2016/YjTSGWepfy/text',
        },
        {
          object_path: '2025/xhBYSpjPAV/passwords',
        },
        {
          object_path: '2001/nr0Edh7dQl/data',
        },
        {
          object_path: '2010/W1icZkS0OT/data',
        },
        {
          object_path: '2023/EJhGkRAgFv/text',
        },
        {
          object_path: '2022/tn895QcVLj/passwords',
        },
        {
          object_path: '2008/IZCrFDN6kG/data',
        },
        {
          object_path: '2012/kUv9Ehw37Q/passwords',
        },
        {
          object_path: '2013/RQyAS9zeoS/data',
        },
        {
          object_path: '2020/YU3i9Iu1HN/data',
        },
        {
          object_path: '2022/JS2gwoPujj/object',
        },
        {
          object_path: '2007/EnBveP5AFa/data',
        },
        {
          object_path: '2005/ZGiyyorje0/data',
        },
        {
          object_path: '2009/YGuvE5RRTA/data',
        },
        {
          object_path: '2003/DqsG2jzJFj/data',
        },
        {
          object_path: '2006/QMoVCuMStr/passwords',
        },
        {
          object_path: '2004/gYOfMNJxJk/text',
        },
        {
          object_path: '2004/GunT2jyMiV/passwords',
        },
        {
          object_path: '2004/H67vC0whFx/object',
        },
        {
          object_path: '2002/UwiCJe06XX/text',
        },
        {
          object_path: '2016/ZgaVv6dIdw/text',
        },
        {
          object_path: '2016/adf7FMk05j/data',
        },
        {
          object_path: '2018/hmDqgqWf5S/object',
        },
        {
          object_path: '2018/4iSdEKEvXc/text',
        },
        {
          object_path: '2015/QdmswqFYI0/object',
        },
        {
          object_path: '2019/M8YofqbETv/passwords',
        },
        {
          object_path: '2021/LiRdw8Ahb5/data',
        },
        {
          object_path: '2024/cDzCawt0aJ/passwords',
        },
        {
          object_path: '2001/l8k6MUUxpD/data',
        },
        {
          object_path: '2018/nbYktHECji/text',
        },
        {
          object_path: '2013/wx8VyjuM8U/object',
        },
        {
          object_path: '2011/Pw93HVUKfx/object',
        },
        {
          object_path: '2006/7wUUpNuTDs/text',
        },
        {
          object_path: '2004/yB7TXeqOga/object',
        },
        {
          object_path: '2025/ZuSs8HbgVe/text',
        },
        {
          object_path: '2003/mlkZmcCM0E/data',
        },
      ],
      off_inventory: false,
    },
    {
      bucket_name: 'testinguseryq78uglinf',
      objects: [
        {
          object_path: '2004/Ga1qxxIb2K/object',
        },
        {
          object_path: '2024/PtiUBKQiY4/text',
        },
        {
          object_path: '2020/DxF8qGADjy/text',
        },
        {
          object_path: '2015/8sTsb9S5JE/text',
        },
        {
          object_path: '2023/vo6GVOJV1f/text',
        },
        {
          object_path: '2023/FVBbe85u6e/object',
        },
        {
          object_path: '2013/mOXjUBOJnQ/passwords',
        },
        {
          object_path: '2003/nNU7kkN9UM/passwords',
        },
        {
          object_path: '2011/2rCYohmuP1/object',
        },
        {
          object_path: '2004/GOfGpowQpi/object',
        },
        {
          object_path: '2000/x1JRAyhAOv/data',
        },
        {
          object_path: '2024/KMtFCflhGP/passwords',
        },
        {
          object_path: '2002/sW5PTjpuAo/passwords',
        },
        {
          object_path: '2007/CTnqyVLgMU/passwords',
        },
        {
          object_path: '2025/eppPTnUWTQ/object',
        },
        {
          object_path: '2008/IGRvH1TVp3/data',
        },
        {
          object_path: '2021/fWqSzN1unW/text',
        },
        {
          object_path: '2019/rIZkYOZEV1/object',
        },
        {
          object_path: '2012/MNJOitHHbg/passwords',
        },
        {
          object_path: '2017/eVZR00Vyi7/data',
        },
        {
          object_path: '2010/eJU6VllV5l/passwords',
        },
        {
          object_path: '2016/4oJEyhCQUc/object',
        },
        {
          object_path: '2005/HczgGQYodd/text',
        },
        {
          object_path: '2001/3pswopT7n5/object',
        },
        {
          object_path: '2006/oFFovnZxll/data',
        },
        {
          object_path: '2023/xYveYM66Ox/data',
        },
        {
          object_path: '2013/fggr0dnN9q/text',
        },
        {
          object_path: '2002/WHlQD68rob/data',
        },
        {
          object_path: '2017/jPkii6fAV8/object',
        },
        {
          object_path: '2003/MuaqFVRjj4/data',
        },
        {
          object_path: '2000/RBcuNmhYF8/text',
        },
        {
          object_path: '2012/8Sp9FBiv09/data',
        },
        {
          object_path: '2015/m3UTQSx7EO/text',
        },
        {
          object_path: '2003/RthD2MF2Yn/text',
        },
        {
          object_path: '2005/R3EPOh1BVY/passwords',
        },
        {
          object_path: '2013/cZ3aIXuUdP/data',
        },
      ],
      off_inventory: false,
    },
    {
      bucket_name: 'stagingaudite9cmwsae5q',
      objects: [
        {
          object_path: '2024/1yWC66Ls0x/object',
        },
        {
          object_path: '2003/LhsLck5b0u/text',
        },
        {
          object_path: '2021/rGuUZqd3lz/passwords',
        },
        {
          object_path: '2006/b89xmL0UPz/object',
        },
        {
          object_path: '2014/LaF8syCFfA/passwords',
        },
        {
          object_path: '2014/kPRbOe5x1k/passwords',
        },
        {
          object_path: '2023/0wlpo8YoDg/passwords',
        },
        {
          object_path: '2023/VjUSgBBwwO/text',
        },
        {
          object_path: '2003/pOsXWK8LUh/passwords',
        },
        {
          object_path: '2002/yf0vKdl3I2/text',
        },
        {
          object_path: '2005/MHkMhdCmNT/text',
        },
        {
          object_path: '2000/C25FIL56D9/passwords',
        },
        {
          object_path: '2016/ojvD2ElrMl/data',
        },
        {
          object_path: '2006/ew51NnUENd/passwords',
        },
        {
          object_path: '2002/qVh3iOYpxR/passwords',
        },
        {
          object_path: '2023/5X2w1AByUJ/text',
        },
        {
          object_path: '2013/UlvTcQejM4/object',
        },
        {
          object_path: '2001/T4M1T9aCwU/data',
        },
        {
          object_path: '2024/aBy6LAQYkf/object',
        },
        {
          object_path: '2008/TaWpxdTkwz/passwords',
        },
        {
          object_path: '2006/DsppvjpGmS/passwords',
        },
        {
          object_path: '2014/4wDjv0SDHE/data',
        },
        {
          object_path: '2019/YcjioPqgsI/object',
        },
        {
          object_path: '2007/Ld7hHUlQ5f/passwords',
        },
        {
          object_path: '2007/bacPsdzgtH/data',
        },
        {
          object_path: '2010/v1HLrikDoK/text',
        },
        {
          object_path: '2016/4GN5O05coV/passwords',
        },
        {
          object_path: '2015/oqsh1a0pdV/passwords',
        },
        {
          object_path: '2006/h66Mh47eNW/data',
        },
        {
          object_path: '2018/ehu436Yj5Z/data',
        },
        {
          object_path: '2009/CwAPi0gpiY/data',
        },
        {
          object_path: '2011/PWfANK64ll/object',
        },
        {
          object_path: '2006/yzG6JcSyNU/data',
        },
        {
          object_path: '2011/XCMWpYLfZm/passwords',
        },
        {
          object_path: '2005/r6OX0s73hv/passwords',
        },
        {
          object_path: '2008/3x4azK0eid/passwords',
        },
        {
          object_path: '2020/n6szSghacx/text',
        },
        {
          object_path: '2008/dhzgmkjWuM/text',
        },
        {
          object_path: '2023/xdHIAyVaRO/object',
        },
        {
          object_path: '2017/2ZQLgYmNlm/data',
        },
        {
          object_path: '2024/6ZlIabBdVd/passwords',
        },
        {
          object_path: '2018/wq1l6epnWC/text',
        },
        {
          object_path: '2011/4vxdIh3iCb/data',
        },
        {
          object_path: '2012/qGUuXXIWoP/text',
        },
        {
          object_path: '2016/MHVqBIc9s0/data',
        },
        {
          object_path: '2014/S5SDwFbmeP/object',
        },
        {
          object_path: '2012/KttkSHThxk/text',
        },
        {
          object_path: '2006/NYQwrVNgZ0/passwords',
        },
        {
          object_path: '2023/9qR0jvJd3Y/object',
        },
        {
          object_path: '2023/kcdAwU422v/data',
        },
        {
          object_path: '2008/O9qSIb8KeD/data',
        },
        {
          object_path: '2003/KoWZfVIq3i/passwords',
        },
        {
          object_path: '2017/z4pzdvXQAS/passwords',
        },
        {
          object_path: '2020/ZYk0AvGe4Q/object',
        },
        {
          object_path: '2012/p97Q7bDm0S/passwords',
        },
        {
          object_path: '2025/qZ3FNvcPPH/text',
        },
        {
          object_path: '2009/S608Db7vHk/object',
        },
        {
          object_path: '2022/zo950QCqqF/data',
        },
        {
          object_path: '2002/8MJ8rhIz1o/passwords',
        },
        {
          object_path: '2004/YChiihjsi8/text',
        },
        {
          object_path: '2005/cB8LiZDK5E/object',
        },
        {
          object_path: '2019/UqFGHfrk59/data',
        },
        {
          object_path: '2007/l7fUjc2s3F/passwords',
        },
        {
          object_path: '2004/0jyXyPVM9Q/object',
        },
        {
          object_path: '2006/j9YMKTt4Su/data',
        },
        {
          object_path: '2015/B0mjqOy9WC/data',
        },
        {
          object_path: '2004/PdEofgHGOF/data',
        },
      ],
      off_inventory: false,
    },
    {
      bucket_name: 'staging-user-88s10ql3g9',
      objects: [
        {
          object_path: '2005/pvUC7gbMy7/object',
        },
        {
          object_path: '2014/7mvaxRgV2c/object',
        },
        {
          object_path: '2022/f6gwzNyGKz/data',
        },
        {
          object_path: '2024/uXUuHh8zfy/passwords',
        },
        {
          object_path: '2004/P1YsHokYdw/data',
        },
        {
          object_path: '2015/mHDACqltMs/passwords',
        },
        {
          object_path: '2020/7P7WIb7juy/text',
        },
        {
          object_path: '2015/Mmo0kEjLKA/passwords',
        },
        {
          object_path: '2007/AbYcrUUSPx/text',
        },
        {
          object_path: '2020/L9xZQ3P64k/passwords',
        },
        {
          object_path: '2015/qh0aczSWDW/text',
        },
        {
          object_path: '2008/PeNBJdcv2K/object',
        },
        {
          object_path: '2014/8sYIiK6UBf/object',
        },
        {
          object_path: '2012/Nl2ePeKDy8/data',
        },
        {
          object_path: '2019/bCQTK3DjtD/passwords',
        },
        {
          object_path: '2022/XJqyP1eraU/passwords',
        },
        {
          object_path: '2007/uODReaq8vb/passwords',
        },
        {
          object_path: '2002/jaoXmVJttY/passwords',
        },
        {
          object_path: '2012/u2fQWijtTs/object',
        },
        {
          object_path: '2013/M1B9wce0Nk/text',
        },
        {
          object_path: '2011/CNztmUmvFT/text',
        },
        {
          object_path: '2004/kjTyknKar5/passwords',
        },
        {
          object_path: '2011/KezQJ1mYHF/text',
        },
        {
          object_path: '2021/IhoA3e2A4A/object',
        },
        {
          object_path: '2008/H9Z4jHTMFG/data',
        },
        {
          object_path: '2011/xQZy2Xexwk/text',
        },
      ],
      off_inventory: false,
    },
    {
      bucket_name: 'staging-customer-bjcg4qempq',
      objects: [
        {
          object_path: '2025/ZpzsaQErDF/object',
        },
        {
          object_path: '2025/Dns50gcfZ8/text',
        },
        {
          object_path: '2000/btc3wVzX9W/passwords',
        },
        {
          object_path: '2002/Alk2W3qRgZ/object',
        },
        {
          object_path: '2021/CkAKdpLS9M/text',
        },
        {
          object_path: '2006/YYGcMrTW4v/data',
        },
        {
          object_path: '2006/WQjmAcGy2w/data',
        },
        {
          object_path: '2012/HWloLPHirk/data',
        },
        {
          object_path: '2015/ra60MRphT7/passwords',
        },
        {
          object_path: '2000/NM6VSgKFnd/passwords',
        },
        {
          object_path: '2005/YkO0JhjaWI/text',
        },
        {
          object_path: '2014/ONnO2u4clg/object',
        },
        {
          object_path: '2014/uU0cL6UFMn/object',
        },
        {
          object_path: '2007/qMvwmIpl4k/passwords',
        },
        {
          object_path: '2010/BES5GcQ2ZN/text',
        },
        {
          object_path: '2015/M9FjQ5Fzj1/text',
        },
        {
          object_path: '2008/nh6z2VdPa8/data',
        },
        {
          object_path: '2013/iLzS4RSDQK/data',
        },
        {
          object_path: '2018/eAD24VrGcb/text',
        },
        {
          object_path: '2023/HkP7skV2Mg/object',
        },
        {
          object_path: '2020/T7QlASf0yN/data',
        },
        {
          object_path: '2019/ZjjhLNhYwf/text',
        },
        {
          object_path: '2006/WSkg7QhQUg/object',
        },
        {
          object_path: '2015/8uqcFaXlZd/data',
        },
        {
          object_path: '2019/V75mXI8rpl/text',
        },
        {
          object_path: '2010/07LVJqCZUA/object',
        },
        {
          object_path: '2002/hMG4eq4CMc/object',
        },
        {
          object_path: '2011/VMTG055e7r/object',
        },
        {
          object_path: '2014/QZg4Jv2YXr/text',
        },
        {
          object_path: '2014/h9iXANpSaz/object',
        },
        {
          object_path: '2001/mK5362NCYu/object',
        },
        {
          object_path: '2022/c2bWF2KOiM/object',
        },
        {
          object_path: '2012/JzeZapCBDc/passwords',
        },
        {
          object_path: '2007/HxDbEdLnmo/passwords',
        },
        {
          object_path: '2015/UKomMXImHI/passwords',
        },
        {
          object_path: '2013/4zNh3198qc/object',
        },
        {
          object_path: '2002/0ORgaiR1bR/text',
        },
        {
          object_path: '2009/9GNd8PfLZX/object',
        },
        {
          object_path: '2002/yNvPerncxN/data',
        },
        {
          object_path: '2002/mHEGhP7XCg/text',
        },
        {
          object_path: '2023/fFtrAhvwuu/text',
        },
        {
          object_path: '2020/6asj4l4c5m/data',
        },
        {
          object_path: '2000/C9qqduKkVu/data',
        },
        {
          object_path: '2024/UOSDz7SA2O/passwords',
        },
        {
          object_path: '2021/bVkIsjuOKw/text',
        },
        {
          object_path: '2001/HFR0jc8w4N/object',
        },
        {
          object_path: '2012/flXnjVjuDx/passwords',
        },
        {
          object_path: '2022/viztYBXYqy/data',
        },
        {
          object_path: '2012/xByDzsu0ej/passwords',
        },
        {
          object_path: '2011/EtXUKmmT7N/passwords',
        },
        {
          object_path: '2003/kOAhRrvMl6/object',
        },
        {
          object_path: '2011/CGHewWysnY/object',
        },
        {
          object_path: '2017/xRFJE9DRVM/object',
        },
        {
          object_path: '2004/O00CaMyfSt/data',
        },
        {
          object_path: '2019/Os27oIDztT/object',
        },
        {
          object_path: '2001/tolnAjm04s/data',
        },
        {
          object_path: '2009/AtA3cube0F/object',
        },
        {
          object_path: '2007/nQ8TjdMiGG/object',
        },
        {
          object_path: '2019/lOHwZD73HP/data',
        },
        {
          object_path: '2002/xqiW5k5Efv/data',
        },
        {
          object_path: '2013/v0Q9E6KLGq/text',
        },
        {
          object_path: '2007/RLqnMNiekf/text',
        },
        {
          object_path: '2014/W2i54tknR3/text',
        },
        {
          object_path: '2010/9efD18mw5b/object',
        },
        {
          object_path: '2004/9tvJyXj8WL/passwords',
        },
        {
          object_path: '2006/fU3qg0D8Hu/passwords',
        },
        {
          object_path: '2005/o2w1s4aAJr/passwords',
        },
        {
          object_path: '2004/cDcUpwlzWV/text',
        },
        {
          object_path: '2008/k7wsKlccwp/object',
        },
        {
          object_path: '2016/WJY4nemZQf/data',
        },
        {
          object_path: '2001/6cSVbqFgxb/passwords',
        },
        {
          object_path: '2013/rX1DVmC86O/passwords',
        },
        {
          object_path: '2021/c4F4nwX18w/text',
        },
        {
          object_path: '2022/i7UBz42xGe/object',
        },
        {
          object_path: '2012/cKPgfhFidX/passwords',
        },
        {
          object_path: '2004/q7TAkGjQpT/object',
        },
        {
          object_path: '2014/f5oCWb1VzL/passwords',
        },
        {
          object_path: '2018/2KyW3bWGz2/data',
        },
        {
          object_path: '2019/4uT7hVVGvs/text',
        },
        {
          object_path: '2020/lMOaIkHsPt/passwords',
        },
        {
          object_path: '2006/RSbWfMaJQ0/text',
        },
        {
          object_path: '2007/fCAVXqWhdB/text',
        },
        {
          object_path: '2015/DwN1CLa20S/text',
        },
        {
          object_path: '2009/QSdyTEIm06/passwords',
        },
        {
          object_path: '2021/QmQOXriv55/object',
        },
        {
          object_path: '2018/5Tb8GDjx0w/text',
        },
      ],
      off_inventory: false,
    },
    {
      bucket_name: 'devcustomergtkbml1db1',
      objects: [
        {
          object_path: '2018/jcbAdbspyI/object',
        },
        {
          object_path: '2017/v9cvvdRCSI/data',
        },
        {
          object_path: '2000/fU7nIEoZd3/passwords',
        },
        {
          object_path: '2000/sM86uiBqCy/passwords',
        },
        {
          object_path: '2023/ub2gUIfUAL/text',
        },
        {
          object_path: '2019/xIT8S72jdy/passwords',
        },
        {
          object_path: '2006/4gqgDtdj6V/data',
        },
        {
          object_path: '2025/QDK2mPfZwr/passwords',
        },
        {
          object_path: '2014/tdsPSWqzqu/object',
        },
        {
          object_path: '2013/3JIGJXoTCM/text',
        },
        {
          object_path: '2019/tI0NrdM5Gn/text',
        },
        {
          object_path: '2013/iBjJqT8PhC/text',
        },
        {
          object_path: '2000/Qe4eZeTxxS/text',
        },
        {
          object_path: '2016/DfFTOcQGpS/object',
        },
        {
          object_path: '2019/NChGveLBCa/data',
        },
        {
          object_path: '2001/cnwNkMCJvu/passwords',
        },
        {
          object_path: '2019/GSiUv7NpLv/data',
        },
        {
          object_path: '2002/h27uocdf0Q/data',
        },
        {
          object_path: '2002/KwPKrZogTh/passwords',
        },
        {
          object_path: '2016/1kY6JBwIE7/data',
        },
        {
          object_path: '2011/H1R5AcpwYx/passwords',
        },
        {
          object_path: '2019/66wLuivRse/data',
        },
        {
          object_path: '2004/9iVjPml15t/data',
        },
        {
          object_path: '2008/SxcMtjZK7y/object',
        },
        {
          object_path: '2006/XH8SSAadAO/object',
        },
        {
          object_path: '2009/SP5RgFVDPt/object',
        },
        {
          object_path: '2005/40HHeuClLA/passwords',
        },
        {
          object_path: '2015/pajMZjhFAD/passwords',
        },
        {
          object_path: '2007/jQXN6JbbJM/data',
        },
        {
          object_path: '2019/chSJFpV1wP/passwords',
        },
        {
          object_path: '2007/k7k1XnKg2j/object',
        },
        {
          object_path: '2003/bapudrmLyW/passwords',
        },
        {
          object_path: '2002/00YSnGb3rA/text',
        },
        {
          object_path: '2025/5Lo6pemFP0/object',
        },
        {
          object_path: '2000/Ev1d7fOoDh/object',
        },
        {
          object_path: '2006/3o4xccF2s2/data',
        },
        {
          object_path: '2014/FiYPVlQRm0/text',
        },
        {
          object_path: '2001/xodPBUsvMH/data',
        },
        {
          object_path: '2016/sdfaYfqFnL/passwords',
        },
        {
          object_path: '2015/9SwhKZLQex/data',
        },
        {
          object_path: '2010/8BM0RANaWw/text',
        },
        {
          object_path: '2024/o9e5dYeufI/text',
        },
        {
          object_path: '2017/9WTIg7GnZW/passwords',
        },
        {
          object_path: '2010/1cjckUaAhV/text',
        },
        {
          object_path: '2011/kCogXUaiIp/passwords',
        },
        {
          object_path: '2009/WX511tKTqF/passwords',
        },
        {
          object_path: '2019/WwAofHDjJb/text',
        },
        {
          object_path: '2025/piQNhM5Nrs/data',
        },
        {
          object_path: '2025/CqRC7eTSol/passwords',
        },
        {
          object_path: '2013/TJwswzzmF5/passwords',
        },
        {
          object_path: '2021/cRy01UlSFm/text',
        },
        {
          object_path: '2014/bd5cayfkH9/text',
        },
        {
          object_path: '2011/fhPLa5uIMJ/data',
        },
        {
          object_path: '2024/1fp3cctP1F/object',
        },
        {
          object_path: '2019/ckkihskg9p/passwords',
        },
        {
          object_path: '2015/0ibQiPw5O9/passwords',
        },
        {
          object_path: '2003/LBX2mpQJn4/passwords',
        },
      ],
      off_inventory: false,
    },
    {
      bucket_name: 'devadminmgs7fk30k9',
      objects: [
        {
          object_path: '2020/ofuL799OC6/passwords',
        },
        {
          object_path: '2002/CldtinEfm5/data',
        },
        {
          object_path: '2003/QQNiQegelz/passwords',
        },
        {
          object_path: '2003/t90MAB5mDs/text',
        },
        {
          object_path: '2010/fmXpHFxA4n/data',
        },
        {
          object_path: '2024/qxpBTLUswK/data',
        },
        {
          object_path: '2023/LLheIftrDM/text',
        },
        {
          object_path: '2015/9dHQa4doBT/data',
        },
        {
          object_path: '2009/rBBCjTdacr/passwords',
        },
        {
          object_path: '2004/1KTsouIIBt/data',
        },
        {
          object_path: '2019/ylgYfhiCUK/data',
        },
        {
          object_path: '2017/xqOTohnx6g/text',
        },
        {
          object_path: '2015/ateHVNruxY/data',
        },
        {
          object_path: '2009/uOKvVE1Nuk/text',
        },
        {
          object_path: '2011/NAqGexezm5/passwords',
        },
        {
          object_path: '2015/nVxcfDDuhy/data',
        },
        {
          object_path: '2011/xcZsxwttOH/data',
        },
        {
          object_path: '2016/m6nSY5HDhi/object',
        },
        {
          object_path: '2024/vLl34CWjDj/object',
        },
        {
          object_path: '2016/6UK1l3Y0zX/data',
        },
        {
          object_path: '2008/qghDbBfdLB/data',
        },
        {
          object_path: '2010/IXTJgb8o2u/passwords',
        },
        {
          object_path: '2002/ihlONDO2Qr/text',
        },
        {
          object_path: '2002/OqHkeFpOUs/data',
        },
        {
          object_path: '2004/mU1kN2ggsu/object',
        },
        {
          object_path: '2003/yiibYF4A3q/passwords',
        },
        {
          object_path: '2008/RjrNClRRMo/passwords',
        },
        {
          object_path: '2021/hWB3r0KzmJ/data',
        },
        {
          object_path: '2023/Kv5iWLog4d/object',
        },
        {
          object_path: '2021/phweciEymK/object',
        },
        {
          object_path: '2008/n8FEqrLA1i/text',
        },
        {
          object_path: '2002/Cub8vdJi74/object',
        },
        {
          object_path: '2019/FOv8bokhXm/object',
        },
        {
          object_path: '2021/EdQk3MBBms/text',
        },
        {
          object_path: '2001/HkTdaK1Elz/object',
        },
        {
          object_path: '2008/1kfVbeHYYP/object',
        },
        {
          object_path: '2018/rQwXTojKpX/data',
        },
        {
          object_path: '2011/zYOO9UfjMv/object',
        },
        {
          object_path: '2015/eEwEDgBmlo/object',
        },
        {
          object_path: '2005/ICAcHUZtd8/passwords',
        },
        {
          object_path: '2021/EHSO8tvAtO/object',
        },
        {
          object_path: '2007/GpiKPCT1rs/passwords',
        },
        {
          object_path: '2006/1fGuI2TzJ4/object',
        },
        {
          object_path: '2012/rKDp66G6Zb/data',
        },
        {
          object_path: '2002/WIt9S1WkGV/data',
        },
        {
          object_path: '2020/QpL4smps05/data',
        },
        {
          object_path: '2024/2bVLX8PAxP/text',
        },
        {
          object_path: '2002/C2ngVrXFK9/passwords',
        },
        {
          object_path: '2011/C1gnkWH3H8/data',
        },
      ],
      off_inventory: false,
    },
    {
      bucket_name: 'dev-audit-qa6lrh6f53',
      objects: [
        {
          object_path: '2001/IwWeUYSeEf/data',
        },
        {
          object_path: '2012/OMH6BSFc2k/passwords',
        },
        {
          object_path: '2016/7kSfudpKPK/passwords',
        },
        {
          object_path: '2003/Z9FBIqPIMG/text',
        },
        {
          object_path: '2010/DE9w9Ze0h7/object',
        },
        {
          object_path: '2017/LMbhJTtQpe/object',
        },
        {
          object_path: '2021/rRdFYDcFXP/object',
        },
        {
          object_path: '2000/RAWRAEOScL/data',
        },
        {
          object_path: '2025/F2Gqb62l0J/text',
        },
      ],
      off_inventory: false,
    },
  ],
  SQSQueue: null,
  SSMParameter: [
    {
      ssm_parameter_name: 'staging-admin-',
      off_inventory: false,
    },
    {
      ssm_parameter_name: 'devadmin',
      off_inventory: false,
    },
    {
      ssm_parameter_name: 'dev_user_',
      off_inventory: false,
    },
    {
      ssm_parameter_name: 'staging_customer_',
      off_inventory: false,
    },
    {
      ssm_parameter_name: 'devaudit',
      off_inventory: false,
    },
    {
      ssm_parameter_name: 'devuser',
      off_inventory: false,
    },
    {
      ssm_parameter_name: 'prod-customer-',
      off_inventory: false,
    },
    {
      ssm_parameter_name: 'prodadmin',
      off_inventory: false,
    },
    {
      ssm_parameter_name: 'prod_admin_',
      off_inventory: false,
    },
  ],
  SecretsManagerSecret: [
    {
      secret_name: 'testingadmin',
      off_inventory: false,
    },
    {
      secret_name: 'staginguser',
      off_inventory: false,
    },
    {
      secret_name: 'prod-customer-',
      off_inventory: false,
    },
    {
      secret_name: 'prod=customer=',
      off_inventory: false,
    },
    {
      secret_name: 'staging@admin@',
      off_inventory: false,
    },
    {
      secret_name: 'prodcustomer',
      off_inventory: false,
    },
    {
      secret_name: 'prod+admin+',
      off_inventory: false,
    },
  ],
  DynamoDBTable: [
    {
      table_name: 'testing_admin_',
      off_inventory: false,
      table_items: [
        'text_9d7w9',
        'object-9qx1l',
        'passwordskai75',
        'passwords_x0ejf',
        'objecty58h1',
        'passwords4jxw3',
        'object-g8isj',
        'data-kri38',
        'passwords-m6vkc',
        'data_d5urt',
        'dataki7xi',
        'textt71wp',
        'text_xvvi8',
        'object_d2xul',
        'object-48b3o',
        'text_wfhbg',
        'object1ig2x',
        'textb828r',
        'data_hqdf2',
        'passwords-g2iym',
        'passwords-tryuz',
        'object-xjct6',
        'data_gvj41',
        'passwords-xbbd0',
        'textt5l5k',
        'text_1m2xu',
        'passwords_6ejnl',
        'data_m0n33',
        'datamy5ix',
        'object-ztzhx',
        'text-0inho',
        'passwords2qspa',
        'text_qfnnr',
        'data5tuhm',
        'text_hsl4s',
        'text-env9w',
        'datag0b0z',
        'text_lbckr',
        'dataccwuq',
        'passwords_jxhfb',
        'data_8muf0',
        'passwordskbezg',
        'objecteflm9',
        'passwords-317iz',
        'data-b03qv',
        'data-jor2p',
        'passwords_362h1',
        'textf5y2j',
        'object_2a9rr',
        'passwords-kafe7',
        'text7ls9n',
        'passwords-lnzhs',
        'object2gx8l',
        'data_uwtuv',
        'text_51uvs',
        'datafj2cl',
        'data_rdlqc',
        'textd6akk',
        'text_daol6',
        'text_nuttr',
        'objectablo4',
        'data4zthj',
        'objectyd92u',
        'textltepg',
        'object8d4et',
        'passwordsuy025',
        'text_xn3ox',
        'data_8ro6x',
        'textnqfn6',
      ],
    },
  ],
});

export const assetsManageExample = ref<ProposedAWSInfraTokenPlanData>({
  S3Bucket: [
    {
      bucket_name: 'devadminmgs7fk30k9',
      objects: [
        {
          object_path: '2020/ofuL799OC6/passwords',
        },
        {
          object_path: '2002/CldtinEfm5/data',
        },
        {
          object_path: '2003/QQNiQegelz/passwords',
        },
        {
          object_path: '2003/t90MAB5mDs/text',
        },
        {
          object_path: '2010/fmXpHFxA4n/data',
        },
        {
          object_path: '2024/qxpBTLUswK/data',
        },
        {
          object_path: '2023/LLheIftrDM/text',
        },
        {
          object_path: '2015/9dHQa4doBT/data',
        },
        {
          object_path: '2009/rBBCjTdacr/passwords',
        },
        {
          object_path: '2004/1KTsouIIBt/data',
        },
        {
          object_path: '2019/ylgYfhiCUK/data',
        },
        {
          object_path: '2017/xqOTohnx6g/text',
        },
        {
          object_path: '2015/ateHVNruxY/data',
        },
        {
          object_path: '2009/uOKvVE1Nuk/text',
        },
        {
          object_path: '2011/NAqGexezm5/passwords',
        },
        {
          object_path: '2015/nVxcfDDuhy/data',
        },
        {
          object_path: '2011/xcZsxwttOH/data',
        },
        {
          object_path: '2016/m6nSY5HDhi/object',
        },
        {
          object_path: '2024/vLl34CWjDj/object',
        },
        {
          object_path: '2016/6UK1l3Y0zX/data',
        },
        {
          object_path: '2008/qghDbBfdLB/data',
        },
        {
          object_path: '2010/IXTJgb8o2u/passwords',
        },
        {
          object_path: '2002/ihlONDO2Qr/text',
        },
        {
          object_path: '2002/OqHkeFpOUs/data',
        },
        {
          object_path: '2004/mU1kN2ggsu/object',
        },
        {
          object_path: '2003/yiibYF4A3q/passwords',
        },
        {
          object_path: '2008/RjrNClRRMo/passwords',
        },
        {
          object_path: '2021/hWB3r0KzmJ/data',
        },
        {
          object_path: '2023/Kv5iWLog4d/object',
        },
        {
          object_path: '2021/phweciEymK/object',
        },
        {
          object_path: '2008/n8FEqrLA1i/text',
        },
        {
          object_path: '2002/Cub8vdJi74/object',
        },
        {
          object_path: '2019/FOv8bokhXm/object',
        },
        {
          object_path: '2021/EdQk3MBBms/text',
        },
        {
          object_path: '2001/HkTdaK1Elz/object',
        },
        {
          object_path: '2008/1kfVbeHYYP/object',
        },
        {
          object_path: '2018/rQwXTojKpX/data',
        },
        {
          object_path: '2011/zYOO9UfjMv/object',
        },
        {
          object_path: '2015/eEwEDgBmlo/object',
        },
        {
          object_path: '2005/ICAcHUZtd8/passwords',
        },
        {
          object_path: '2021/EHSO8tvAtO/object',
        },
        {
          object_path: '2007/GpiKPCT1rs/passwords',
        },
        {
          object_path: '2006/1fGuI2TzJ4/object',
        },
        {
          object_path: '2012/rKDp66G6Zb/data',
        },
        {
          object_path: '2002/WIt9S1WkGV/data',
        },
        {
          object_path: '2020/QpL4smps05/data',
        },
        {
          object_path: '2024/2bVLX8PAxP/text',
        },
        {
          object_path: '2002/C2ngVrXFK9/passwords',
        },
        {
          object_path: '2011/C1gnkWH3H8/data',
        },
      ],
      off_inventory: true,
    },
    {
      bucket_name: 'dev-audit-qa6lrh6f53',
      objects: [
        {
          object_path: '2001/IwWeUYSeEf/data',
        },
        {
          object_path: '2012/OMH6BSFc2k/passwords',
        },
        {
          object_path: '2016/7kSfudpKPK/passwords',
        },
        {
          object_path: '2003/Z9FBIqPIMG/text',
        },
        {
          object_path: '2010/DE9w9Ze0h7/object',
        },
        {
          object_path: '2017/LMbhJTtQpe/object',
        },
        {
          object_path: '2021/rRdFYDcFXP/object',
        },
        {
          object_path: '2000/RAWRAEOScL/data',
        },
        {
          object_path: '2025/F2Gqb62l0J/text',
        },
      ],
      off_inventory: true,
    },
  ],
  SQSQueue: [
    {
      sqs_queue_name: 'testing_admin_',
      off_inventory: true,
    },
    {
      sqs_queue_name: 'prod-admin-',
      off_inventory: true,
    },
    {
      sqs_queue_name: 'prod_audit_',
      off_inventory: true,
    },
    {
      sqs_queue_name: 'staginguser',
      off_inventory: true,
    },
    {
      sqs_queue_name: 'dev-audit-',
      off_inventory: true,
    },
    {
      sqs_queue_name: 'staging-audit-',
      off_inventory: true,
    },
    {
      sqs_queue_name: 'dev_user_',
      off_inventory: true,
    },
  ],
  SSMParameter: [
    {
      ssm_parameter_name: 'staging-admin-',
      off_inventory: true,
    },
    {
      ssm_parameter_name: 'devadmin',
      off_inventory: true,
    },
    {
      ssm_parameter_name: 'dev_user_',
      off_inventory: true,
    },
    {
      ssm_parameter_name: 'staging_customer_',
      off_inventory: true,
    },
    {
      ssm_parameter_name: 'devaudit',
      off_inventory: true,
    },
    {
      ssm_parameter_name: 'devuser',
      off_inventory: true,
    },
    {
      ssm_parameter_name: 'prod-customer-',
      off_inventory: false,
    },
    {
      ssm_parameter_name: 'prodadmin',
      off_inventory: false,
    },
    {
      ssm_parameter_name: 'prod_admin_',
      off_inventory: false,
    },
  ],
  SecretsManagerSecret: [
    {
      secret_name: 'testingadmin',
      off_inventory: true,
    },
    {
      secret_name: 'staginguser',
      off_inventory: true,
    },
    {
      secret_name: 'prod-customer-',
      off_inventory: true,
    },
    {
      secret_name: 'prod=customer=',
      off_inventory: true,
    },
    {
      secret_name: 'staging@admin@',
      off_inventory: true,
    },
    {
      secret_name: 'prodcustomer',
      off_inventory: true,
    },
    {
      secret_name: 'prod+admin+',
      off_inventory: true,
    },
  ],
  DynamoDBTable: [
    {
      table_name: 'testing_admin_',
      off_inventory: true,
      table_items: [
        'text_9d7w9',
        'object-9qx1l',
        'passwordskai75',
        'passwords_x0ejf',
        'objecty58h1',
        'passwords4jxw3',
        'object-g8isj',
        'data-kri38',
        'passwords-m6vkc',
        'data_d5urt',
        'dataki7xi',
        'textt71wp',
        'text_xvvi8',
        'object_d2xul',
        'object-48b3o',
        'text_wfhbg',
        'object1ig2x',
        'textb828r',
        'data_hqdf2',
        'passwords-g2iym',
        'passwords-tryuz',
        'object-xjct6',
        'data_gvj41',
        'passwords-xbbd0',
        'textt5l5k',
        'text_1m2xu',
        'passwords_6ejnl',
        'data_m0n33',
        'datamy5ix',
        'object-ztzhx',
        'text-0inho',
        'passwords2qspa',
        'text_qfnnr',
        'data5tuhm',
        'text_hsl4s',
        'text-env9w',
        'datag0b0z',
        'text_lbckr',
        'dataccwuq',
        'passwords_jxhfb',
        'data_8muf0',
        'passwordskbezg',
        'objecteflm9',
        'passwords-317iz',
        'data-b03qv',
        'data-jor2p',
        'passwords_362h1',
        'textf5y2j',
        'object_2a9rr',
        'passwords-kafe7',
        'text7ls9n',
        'passwords-lnzhs',
        'object2gx8l',
        'data_uwtuv',
        'text_51uvs',
        'datafj2cl',
        'data_rdlqc',
        'textd6akk',
        'text_daol6',
        'text_nuttr',
        'objectablo4',
        'data4zthj',
        'objectyd92u',
        'textltepg',
        'object8d4et',
        'passwordsuy025',
        'text_xn3ox',
        'data_8ro6x',
        'textnqfn6',
      ],
    },
  ],
});

export const assetInitialEmptyParameter = ref<ProposedAWSInfraTokenPlanData>({
  S3Bucket: [
    {
      bucket_name: 'stagingcustomersab5rcqvgz',
      objects: [
        {
          object_path: '2016/9y6MmQsbxg/object',
        },
        {
          object_path: '2012/4guCu7i4kU/object',
        },
        {
          object_path: '2017/tIJXkV2zU9/text',
        },
        {
          object_path: '2022/w1hWemKszJ/passwords',
        },
        {
          object_path: '2016/YqkZZMKvCr/passwords',
        },
        {
          object_path: '2003/9hfbHNqxlC/object',
        },
        {
          object_path: '2005/kTwM5c8lx2/text',
        },
        {
          object_path: '2011/OJVkCTiYNi/passwords',
        },
        {
          object_path: '2009/uXTk29uqsj/object',
        },
        {
          object_path: '2004/XLjRDbnTdQ/object',
        },
        {
          object_path: '2005/6QgmMfrhTg/passwords',
        },
        {
          object_path: '2014/sZRd7XM6PP/data',
        },
        {
          object_path: '2016/YjTSGWepfy/text',
        },
        {
          object_path: '2025/xhBYSpjPAV/passwords',
        },
        {
          object_path: '2001/nr0Edh7dQl/data',
        },
        {
          object_path: '2010/W1icZkS0OT/data',
        },
        {
          object_path: '2023/EJhGkRAgFv/text',
        },
        {
          object_path: '2022/tn895QcVLj/passwords',
        },
        {
          object_path: '2008/IZCrFDN6kG/data',
        },
        {
          object_path: '2012/kUv9Ehw37Q/passwords',
        },
        {
          object_path: '2013/RQyAS9zeoS/data',
        },
        {
          object_path: '2020/YU3i9Iu1HN/data',
        },
        {
          object_path: '2022/JS2gwoPujj/object',
        },
        {
          object_path: '2007/EnBveP5AFa/data',
        },
        {
          object_path: '2005/ZGiyyorje0/data',
        },
        {
          object_path: '2009/YGuvE5RRTA/data',
        },
        {
          object_path: '2003/DqsG2jzJFj/data',
        },
        {
          object_path: '2006/QMoVCuMStr/passwords',
        },
        {
          object_path: '2004/gYOfMNJxJk/text',
        },
        {
          object_path: '2004/GunT2jyMiV/passwords',
        },
        {
          object_path: '2004/H67vC0whFx/object',
        },
        {
          object_path: '2002/UwiCJe06XX/text',
        },
        {
          object_path: '2016/ZgaVv6dIdw/text',
        },
        {
          object_path: '2016/adf7FMk05j/data',
        },
        {
          object_path: '2018/hmDqgqWf5S/object',
        },
        {
          object_path: '2018/4iSdEKEvXc/text',
        },
        {
          object_path: '2015/QdmswqFYI0/object',
        },
        {
          object_path: '2019/M8YofqbETv/passwords',
        },
        {
          object_path: '2021/LiRdw8Ahb5/data',
        },
        {
          object_path: '2024/cDzCawt0aJ/passwords',
        },
        {
          object_path: '2001/l8k6MUUxpD/data',
        },
        {
          object_path: '2018/nbYktHECji/text',
        },
        {
          object_path: '2013/wx8VyjuM8U/object',
        },
        {
          object_path: '2011/Pw93HVUKfx/object',
        },
        {
          object_path: '2006/7wUUpNuTDs/text',
        },
        {
          object_path: '2004/yB7TXeqOga/object',
        },
        {
          object_path: '2025/ZuSs8HbgVe/text',
        },
        {
          object_path: '2003/mlkZmcCM0E/data',
        },
      ],
      off_inventory: false,
    },
    {
      bucket_name: 'testinguseryq78uglinf',
      objects: [
        {
          object_path: '2004/Ga1qxxIb2K/object',
        },
        {
          object_path: '2024/PtiUBKQiY4/text',
        },
        {
          object_path: '2020/DxF8qGADjy/text',
        },
        {
          object_path: '2015/8sTsb9S5JE/text',
        },
        {
          object_path: '2023/vo6GVOJV1f/text',
        },
        {
          object_path: '2023/FVBbe85u6e/object',
        },
        {
          object_path: '2013/mOXjUBOJnQ/passwords',
        },
        {
          object_path: '2003/nNU7kkN9UM/passwords',
        },
        {
          object_path: '2011/2rCYohmuP1/object',
        },
        {
          object_path: '2004/GOfGpowQpi/object',
        },
        {
          object_path: '2000/x1JRAyhAOv/data',
        },
        {
          object_path: '2024/KMtFCflhGP/passwords',
        },
        {
          object_path: '2002/sW5PTjpuAo/passwords',
        },
        {
          object_path: '2007/CTnqyVLgMU/passwords',
        },
        {
          object_path: '2025/eppPTnUWTQ/object',
        },
        {
          object_path: '2008/IGRvH1TVp3/data',
        },
        {
          object_path: '2021/fWqSzN1unW/text',
        },
        {
          object_path: '2019/rIZkYOZEV1/object',
        },
        {
          object_path: '2012/MNJOitHHbg/passwords',
        },
        {
          object_path: '2017/eVZR00Vyi7/data',
        },
        {
          object_path: '2010/eJU6VllV5l/passwords',
        },
        {
          object_path: '2016/4oJEyhCQUc/object',
        },
        {
          object_path: '2005/HczgGQYodd/text',
        },
        {
          object_path: '2001/3pswopT7n5/object',
        },
        {
          object_path: '2006/oFFovnZxll/data',
        },
        {
          object_path: '2023/xYveYM66Ox/data',
        },
        {
          object_path: '2013/fggr0dnN9q/text',
        },
        {
          object_path: '2002/WHlQD68rob/data',
        },
        {
          object_path: '2017/jPkii6fAV8/object',
        },
        {
          object_path: '2003/MuaqFVRjj4/data',
        },
        {
          object_path: '2000/RBcuNmhYF8/text',
        },
        {
          object_path: '2012/8Sp9FBiv09/data',
        },
        {
          object_path: '2015/m3UTQSx7EO/text',
        },
        {
          object_path: '2003/RthD2MF2Yn/text',
        },
        {
          object_path: '2005/R3EPOh1BVY/passwords',
        },
        {
          object_path: '2013/cZ3aIXuUdP/data',
        },
      ],
      off_inventory: false,
    },
    {
      bucket_name: 'stagingaudite9cmwsae5q',
      objects: [
        {
          object_path: '2024/1yWC66Ls0x/object',
        },
        {
          object_path: '2003/LhsLck5b0u/text',
        },
        {
          object_path: '2021/rGuUZqd3lz/passwords',
        },
        {
          object_path: '2006/b89xmL0UPz/object',
        },
        {
          object_path: '2014/LaF8syCFfA/passwords',
        },
        {
          object_path: '2014/kPRbOe5x1k/passwords',
        },
        {
          object_path: '2023/0wlpo8YoDg/passwords',
        },
        {
          object_path: '2023/VjUSgBBwwO/text',
        },
        {
          object_path: '2003/pOsXWK8LUh/passwords',
        },
        {
          object_path: '2002/yf0vKdl3I2/text',
        },
        {
          object_path: '2005/MHkMhdCmNT/text',
        },
        {
          object_path: '2000/C25FIL56D9/passwords',
        },
        {
          object_path: '2016/ojvD2ElrMl/data',
        },
        {
          object_path: '2006/ew51NnUENd/passwords',
        },
        {
          object_path: '2002/qVh3iOYpxR/passwords',
        },
        {
          object_path: '2023/5X2w1AByUJ/text',
        },
        {
          object_path: '2013/UlvTcQejM4/object',
        },
        {
          object_path: '2001/T4M1T9aCwU/data',
        },
        {
          object_path: '2024/aBy6LAQYkf/object',
        },
        {
          object_path: '2008/TaWpxdTkwz/passwords',
        },
        {
          object_path: '2006/DsppvjpGmS/passwords',
        },
        {
          object_path: '2014/4wDjv0SDHE/data',
        },
        {
          object_path: '2019/YcjioPqgsI/object',
        },
        {
          object_path: '2007/Ld7hHUlQ5f/passwords',
        },
        {
          object_path: '2007/bacPsdzgtH/data',
        },
        {
          object_path: '2010/v1HLrikDoK/text',
        },
        {
          object_path: '2016/4GN5O05coV/passwords',
        },
        {
          object_path: '2015/oqsh1a0pdV/passwords',
        },
        {
          object_path: '2006/h66Mh47eNW/data',
        },
        {
          object_path: '2018/ehu436Yj5Z/data',
        },
        {
          object_path: '2009/CwAPi0gpiY/data',
        },
        {
          object_path: '2011/PWfANK64ll/object',
        },
        {
          object_path: '2006/yzG6JcSyNU/data',
        },
        {
          object_path: '2011/XCMWpYLfZm/passwords',
        },
        {
          object_path: '2005/r6OX0s73hv/passwords',
        },
        {
          object_path: '2008/3x4azK0eid/passwords',
        },
        {
          object_path: '2020/n6szSghacx/text',
        },
        {
          object_path: '2008/dhzgmkjWuM/text',
        },
        {
          object_path: '2023/xdHIAyVaRO/object',
        },
        {
          object_path: '2017/2ZQLgYmNlm/data',
        },
        {
          object_path: '2024/6ZlIabBdVd/passwords',
        },
        {
          object_path: '2018/wq1l6epnWC/text',
        },
        {
          object_path: '2011/4vxdIh3iCb/data',
        },
        {
          object_path: '2012/qGUuXXIWoP/text',
        },
        {
          object_path: '2016/MHVqBIc9s0/data',
        },
        {
          object_path: '2014/S5SDwFbmeP/object',
        },
        {
          object_path: '2012/KttkSHThxk/text',
        },
        {
          object_path: '2006/NYQwrVNgZ0/passwords',
        },
        {
          object_path: '2023/9qR0jvJd3Y/object',
        },
        {
          object_path: '2023/kcdAwU422v/data',
        },
        {
          object_path: '2008/O9qSIb8KeD/data',
        },
        {
          object_path: '2003/KoWZfVIq3i/passwords',
        },
        {
          object_path: '2017/z4pzdvXQAS/passwords',
        },
        {
          object_path: '2020/ZYk0AvGe4Q/object',
        },
        {
          object_path: '2012/p97Q7bDm0S/passwords',
        },
        {
          object_path: '2025/qZ3FNvcPPH/text',
        },
        {
          object_path: '2009/S608Db7vHk/object',
        },
        {
          object_path: '2022/zo950QCqqF/data',
        },
        {
          object_path: '2002/8MJ8rhIz1o/passwords',
        },
        {
          object_path: '2004/YChiihjsi8/text',
        },
        {
          object_path: '2005/cB8LiZDK5E/object',
        },
        {
          object_path: '2019/UqFGHfrk59/data',
        },
        {
          object_path: '2007/l7fUjc2s3F/passwords',
        },
        {
          object_path: '2004/0jyXyPVM9Q/object',
        },
        {
          object_path: '2006/j9YMKTt4Su/data',
        },
        {
          object_path: '2015/B0mjqOy9WC/data',
        },
        {
          object_path: '2004/PdEofgHGOF/data',
        },
      ],
      off_inventory: false,
    },
    {
      bucket_name: 'staging-user-88s10ql3g9',
      objects: [
        {
          object_path: '2005/pvUC7gbMy7/object',
        },
        {
          object_path: '2014/7mvaxRgV2c/object',
        },
        {
          object_path: '2022/f6gwzNyGKz/data',
        },
        {
          object_path: '2024/uXUuHh8zfy/passwords',
        },
        {
          object_path: '2004/P1YsHokYdw/data',
        },
        {
          object_path: '2015/mHDACqltMs/passwords',
        },
        {
          object_path: '2020/7P7WIb7juy/text',
        },
        {
          object_path: '2015/Mmo0kEjLKA/passwords',
        },
        {
          object_path: '2007/AbYcrUUSPx/text',
        },
        {
          object_path: '2020/L9xZQ3P64k/passwords',
        },
        {
          object_path: '2015/qh0aczSWDW/text',
        },
        {
          object_path: '2008/PeNBJdcv2K/object',
        },
        {
          object_path: '2014/8sYIiK6UBf/object',
        },
        {
          object_path: '2012/Nl2ePeKDy8/data',
        },
        {
          object_path: '2019/bCQTK3DjtD/passwords',
        },
        {
          object_path: '2022/XJqyP1eraU/passwords',
        },
        {
          object_path: '2007/uODReaq8vb/passwords',
        },
        {
          object_path: '2002/jaoXmVJttY/passwords',
        },
        {
          object_path: '2012/u2fQWijtTs/object',
        },
        {
          object_path: '2013/M1B9wce0Nk/text',
        },
        {
          object_path: '2011/CNztmUmvFT/text',
        },
        {
          object_path: '2004/kjTyknKar5/passwords',
        },
        {
          object_path: '2011/KezQJ1mYHF/text',
        },
        {
          object_path: '2021/IhoA3e2A4A/object',
        },
        {
          object_path: '2008/H9Z4jHTMFG/data',
        },
        {
          object_path: '2011/xQZy2Xexwk/text',
        },
      ],
      off_inventory: false,
    },
    {
      bucket_name: 'staging-customer-bjcg4qempq',
      objects: [
        {
          object_path: '2025/ZpzsaQErDF/object',
        },
        {
          object_path: '2025/Dns50gcfZ8/text',
        },
        {
          object_path: '2000/btc3wVzX9W/passwords',
        },
        {
          object_path: '2002/Alk2W3qRgZ/object',
        },
        {
          object_path: '2021/CkAKdpLS9M/text',
        },
        {
          object_path: '2006/YYGcMrTW4v/data',
        },
        {
          object_path: '2006/WQjmAcGy2w/data',
        },
        {
          object_path: '2012/HWloLPHirk/data',
        },
        {
          object_path: '2015/ra60MRphT7/passwords',
        },
        {
          object_path: '2000/NM6VSgKFnd/passwords',
        },
        {
          object_path: '2005/YkO0JhjaWI/text',
        },
        {
          object_path: '2014/ONnO2u4clg/object',
        },
        {
          object_path: '2014/uU0cL6UFMn/object',
        },
        {
          object_path: '2007/qMvwmIpl4k/passwords',
        },
        {
          object_path: '2010/BES5GcQ2ZN/text',
        },
        {
          object_path: '2015/M9FjQ5Fzj1/text',
        },
        {
          object_path: '2008/nh6z2VdPa8/data',
        },
        {
          object_path: '2013/iLzS4RSDQK/data',
        },
        {
          object_path: '2018/eAD24VrGcb/text',
        },
        {
          object_path: '2023/HkP7skV2Mg/object',
        },
        {
          object_path: '2020/T7QlASf0yN/data',
        },
        {
          object_path: '2019/ZjjhLNhYwf/text',
        },
        {
          object_path: '2006/WSkg7QhQUg/object',
        },
        {
          object_path: '2015/8uqcFaXlZd/data',
        },
        {
          object_path: '2019/V75mXI8rpl/text',
        },
        {
          object_path: '2010/07LVJqCZUA/object',
        },
        {
          object_path: '2002/hMG4eq4CMc/object',
        },
        {
          object_path: '2011/VMTG055e7r/object',
        },
        {
          object_path: '2014/QZg4Jv2YXr/text',
        },
        {
          object_path: '2014/h9iXANpSaz/object',
        },
        {
          object_path: '2001/mK5362NCYu/object',
        },
        {
          object_path: '2022/c2bWF2KOiM/object',
        },
        {
          object_path: '2012/JzeZapCBDc/passwords',
        },
        {
          object_path: '2007/HxDbEdLnmo/passwords',
        },
        {
          object_path: '2015/UKomMXImHI/passwords',
        },
        {
          object_path: '2013/4zNh3198qc/object',
        },
        {
          object_path: '2002/0ORgaiR1bR/text',
        },
        {
          object_path: '2009/9GNd8PfLZX/object',
        },
        {
          object_path: '2002/yNvPerncxN/data',
        },
        {
          object_path: '2002/mHEGhP7XCg/text',
        },
        {
          object_path: '2023/fFtrAhvwuu/text',
        },
        {
          object_path: '2020/6asj4l4c5m/data',
        },
        {
          object_path: '2000/C9qqduKkVu/data',
        },
        {
          object_path: '2024/UOSDz7SA2O/passwords',
        },
        {
          object_path: '2021/bVkIsjuOKw/text',
        },
        {
          object_path: '2001/HFR0jc8w4N/object',
        },
        {
          object_path: '2012/flXnjVjuDx/passwords',
        },
        {
          object_path: '2022/viztYBXYqy/data',
        },
        {
          object_path: '2012/xByDzsu0ej/passwords',
        },
        {
          object_path: '2011/EtXUKmmT7N/passwords',
        },
        {
          object_path: '2003/kOAhRrvMl6/object',
        },
        {
          object_path: '2011/CGHewWysnY/object',
        },
        {
          object_path: '2017/xRFJE9DRVM/object',
        },
        {
          object_path: '2004/O00CaMyfSt/data',
        },
        {
          object_path: '2019/Os27oIDztT/object',
        },
        {
          object_path: '2001/tolnAjm04s/data',
        },
        {
          object_path: '2009/AtA3cube0F/object',
        },
        {
          object_path: '2007/nQ8TjdMiGG/object',
        },
        {
          object_path: '2019/lOHwZD73HP/data',
        },
        {
          object_path: '2002/xqiW5k5Efv/data',
        },
        {
          object_path: '2013/v0Q9E6KLGq/text',
        },
        {
          object_path: '2007/RLqnMNiekf/text',
        },
        {
          object_path: '2014/W2i54tknR3/text',
        },
        {
          object_path: '2010/9efD18mw5b/object',
        },
        {
          object_path: '2004/9tvJyXj8WL/passwords',
        },
        {
          object_path: '2006/fU3qg0D8Hu/passwords',
        },
        {
          object_path: '2005/o2w1s4aAJr/passwords',
        },
        {
          object_path: '2004/cDcUpwlzWV/text',
        },
        {
          object_path: '2008/k7wsKlccwp/object',
        },
        {
          object_path: '2016/WJY4nemZQf/data',
        },
        {
          object_path: '2001/6cSVbqFgxb/passwords',
        },
        {
          object_path: '2013/rX1DVmC86O/passwords',
        },
        {
          object_path: '2021/c4F4nwX18w/text',
        },
        {
          object_path: '2022/i7UBz42xGe/object',
        },
        {
          object_path: '2012/cKPgfhFidX/passwords',
        },
        {
          object_path: '2004/q7TAkGjQpT/object',
        },
        {
          object_path: '2014/f5oCWb1VzL/passwords',
        },
        {
          object_path: '2018/2KyW3bWGz2/data',
        },
        {
          object_path: '2019/4uT7hVVGvs/text',
        },
        {
          object_path: '2020/lMOaIkHsPt/passwords',
        },
        {
          object_path: '2006/RSbWfMaJQ0/text',
        },
        {
          object_path: '2007/fCAVXqWhdB/text',
        },
        {
          object_path: '2015/DwN1CLa20S/text',
        },
        {
          object_path: '2009/QSdyTEIm06/passwords',
        },
        {
          object_path: '2021/QmQOXriv55/object',
        },
        {
          object_path: '2018/5Tb8GDjx0w/text',
        },
      ],
      off_inventory: false,
    },
    {
      bucket_name: 'devcustomergtkbml1db1',
      objects: [
        {
          object_path: '2018/jcbAdbspyI/object',
        },
        {
          object_path: '2017/v9cvvdRCSI/data',
        },
        {
          object_path: '2000/fU7nIEoZd3/passwords',
        },
        {
          object_path: '2000/sM86uiBqCy/passwords',
        },
        {
          object_path: '2023/ub2gUIfUAL/text',
        },
        {
          object_path: '2019/xIT8S72jdy/passwords',
        },
        {
          object_path: '2006/4gqgDtdj6V/data',
        },
        {
          object_path: '2025/QDK2mPfZwr/passwords',
        },
        {
          object_path: '2014/tdsPSWqzqu/object',
        },
        {
          object_path: '2013/3JIGJXoTCM/text',
        },
        {
          object_path: '2019/tI0NrdM5Gn/text',
        },
        {
          object_path: '2013/iBjJqT8PhC/text',
        },
        {
          object_path: '2000/Qe4eZeTxxS/text',
        },
        {
          object_path: '2016/DfFTOcQGpS/object',
        },
        {
          object_path: '2019/NChGveLBCa/data',
        },
        {
          object_path: '2001/cnwNkMCJvu/passwords',
        },
        {
          object_path: '2019/GSiUv7NpLv/data',
        },
        {
          object_path: '2002/h27uocdf0Q/data',
        },
        {
          object_path: '2002/KwPKrZogTh/passwords',
        },
        {
          object_path: '2016/1kY6JBwIE7/data',
        },
        {
          object_path: '2011/H1R5AcpwYx/passwords',
        },
        {
          object_path: '2019/66wLuivRse/data',
        },
        {
          object_path: '2004/9iVjPml15t/data',
        },
        {
          object_path: '2008/SxcMtjZK7y/object',
        },
        {
          object_path: '2006/XH8SSAadAO/object',
        },
        {
          object_path: '2009/SP5RgFVDPt/object',
        },
        {
          object_path: '2005/40HHeuClLA/passwords',
        },
        {
          object_path: '2015/pajMZjhFAD/passwords',
        },
        {
          object_path: '2007/jQXN6JbbJM/data',
        },
        {
          object_path: '2019/chSJFpV1wP/passwords',
        },
        {
          object_path: '2007/k7k1XnKg2j/object',
        },
        {
          object_path: '2003/bapudrmLyW/passwords',
        },
        {
          object_path: '2002/00YSnGb3rA/text',
        },
        {
          object_path: '2025/5Lo6pemFP0/object',
        },
        {
          object_path: '2000/Ev1d7fOoDh/object',
        },
        {
          object_path: '2006/3o4xccF2s2/data',
        },
        {
          object_path: '2014/FiYPVlQRm0/text',
        },
        {
          object_path: '2001/xodPBUsvMH/data',
        },
        {
          object_path: '2016/sdfaYfqFnL/passwords',
        },
        {
          object_path: '2015/9SwhKZLQex/data',
        },
        {
          object_path: '2010/8BM0RANaWw/text',
        },
        {
          object_path: '2024/o9e5dYeufI/text',
        },
        {
          object_path: '2017/9WTIg7GnZW/passwords',
        },
        {
          object_path: '2010/1cjckUaAhV/text',
        },
        {
          object_path: '2011/kCogXUaiIp/passwords',
        },
        {
          object_path: '2009/WX511tKTqF/passwords',
        },
        {
          object_path: '2019/WwAofHDjJb/text',
        },
        {
          object_path: '2025/piQNhM5Nrs/data',
        },
        {
          object_path: '2025/CqRC7eTSol/passwords',
        },
        {
          object_path: '2013/TJwswzzmF5/passwords',
        },
        {
          object_path: '2021/cRy01UlSFm/text',
        },
        {
          object_path: '2014/bd5cayfkH9/text',
        },
        {
          object_path: '2011/fhPLa5uIMJ/data',
        },
        {
          object_path: '2024/1fp3cctP1F/object',
        },
        {
          object_path: '2019/ckkihskg9p/passwords',
        },
        {
          object_path: '2015/0ibQiPw5O9/passwords',
        },
        {
          object_path: '2003/LBX2mpQJn4/passwords',
        },
      ],
      off_inventory: false,
    },
    {
      bucket_name: 'devadminmgs7fk30k9',
      objects: [
        {
          object_path: '2020/ofuL799OC6/passwords',
        },
        {
          object_path: '2002/CldtinEfm5/data',
        },
        {
          object_path: '2003/QQNiQegelz/passwords',
        },
        {
          object_path: '2003/t90MAB5mDs/text',
        },
        {
          object_path: '2010/fmXpHFxA4n/data',
        },
        {
          object_path: '2024/qxpBTLUswK/data',
        },
        {
          object_path: '2023/LLheIftrDM/text',
        },
        {
          object_path: '2015/9dHQa4doBT/data',
        },
        {
          object_path: '2009/rBBCjTdacr/passwords',
        },
        {
          object_path: '2004/1KTsouIIBt/data',
        },
        {
          object_path: '2019/ylgYfhiCUK/data',
        },
        {
          object_path: '2017/xqOTohnx6g/text',
        },
        {
          object_path: '2015/ateHVNruxY/data',
        },
        {
          object_path: '2009/uOKvVE1Nuk/text',
        },
        {
          object_path: '2011/NAqGexezm5/passwords',
        },
        {
          object_path: '2015/nVxcfDDuhy/data',
        },
        {
          object_path: '2011/xcZsxwttOH/data',
        },
        {
          object_path: '2016/m6nSY5HDhi/object',
        },
        {
          object_path: '2024/vLl34CWjDj/object',
        },
        {
          object_path: '2016/6UK1l3Y0zX/data',
        },
        {
          object_path: '2008/qghDbBfdLB/data',
        },
        {
          object_path: '2010/IXTJgb8o2u/passwords',
        },
        {
          object_path: '2002/ihlONDO2Qr/text',
        },
        {
          object_path: '2002/OqHkeFpOUs/data',
        },
        {
          object_path: '2004/mU1kN2ggsu/object',
        },
        {
          object_path: '2003/yiibYF4A3q/passwords',
        },
        {
          object_path: '2008/RjrNClRRMo/passwords',
        },
        {
          object_path: '2021/hWB3r0KzmJ/data',
        },
        {
          object_path: '2023/Kv5iWLog4d/object',
        },
        {
          object_path: '2021/phweciEymK/object',
        },
        {
          object_path: '2008/n8FEqrLA1i/text',
        },
        {
          object_path: '2002/Cub8vdJi74/object',
        },
        {
          object_path: '2019/FOv8bokhXm/object',
        },
        {
          object_path: '2021/EdQk3MBBms/text',
        },
        {
          object_path: '2001/HkTdaK1Elz/object',
        },
        {
          object_path: '2008/1kfVbeHYYP/object',
        },
        {
          object_path: '2018/rQwXTojKpX/data',
        },
        {
          object_path: '2011/zYOO9UfjMv/object',
        },
        {
          object_path: '2015/eEwEDgBmlo/object',
        },
        {
          object_path: '2005/ICAcHUZtd8/passwords',
        },
        {
          object_path: '2021/EHSO8tvAtO/object',
        },
        {
          object_path: '2007/GpiKPCT1rs/passwords',
        },
        {
          object_path: '2006/1fGuI2TzJ4/object',
        },
        {
          object_path: '2012/rKDp66G6Zb/data',
        },
        {
          object_path: '2002/WIt9S1WkGV/data',
        },
        {
          object_path: '2020/QpL4smps05/data',
        },
        {
          object_path: '2024/2bVLX8PAxP/text',
        },
        {
          object_path: '2002/C2ngVrXFK9/passwords',
        },
        {
          object_path: '2011/C1gnkWH3H8/data',
        },
      ],
      off_inventory: false,
    },
    {
      bucket_name: 'dev-audit-qa6lrh6f53',
      objects: [
        {
          object_path: '2001/IwWeUYSeEf/data',
        },
        {
          object_path: '2012/OMH6BSFc2k/passwords',
        },
        {
          object_path: '2016/7kSfudpKPK/passwords',
        },
        {
          object_path: '2003/Z9FBIqPIMG/text',
        },
        {
          object_path: '2010/DE9w9Ze0h7/object',
        },
        {
          object_path: '2017/LMbhJTtQpe/object',
        },
        {
          object_path: '2021/rRdFYDcFXP/object',
        },
        {
          object_path: '2000/RAWRAEOScL/data',
        },
        {
          object_path: '2025/F2Gqb62l0J/text',
        },
      ],
      off_inventory: false,
    },
  ],
  SQSQueue: [
    {
      sqs_queue_name: 'testing_admin_',
      off_inventory: false,
    },
    {
      sqs_queue_name: 'prod-admin-',
      off_inventory: false,
    },
    {
      sqs_queue_name: 'prod_audit_',
      off_inventory: false,
    },
    {
      sqs_queue_name: 'staginguser',
      off_inventory: false,
    },
    {
      sqs_queue_name: 'dev-audit-',
      off_inventory: false,
    },
    {
      sqs_queue_name: 'staging-audit-',
      off_inventory: false,
    },
    {
      sqs_queue_name: 'dev_user_',
      off_inventory: false,
    },
  ],
  SSMParameter: [
    {
      ssm_parameter_name: 'staging-admin-',
      off_inventory: false,
    },
    {
      ssm_parameter_name: 'devadmin',
      off_inventory: false,
    },
    {
      ssm_parameter_name: 'dev_user_',
      off_inventory: false,
    },
    {
      ssm_parameter_name: 'staging_customer_',
      off_inventory: false,
    },
    {
      ssm_parameter_name: 'devaudit',
      off_inventory: false,
    },
    {
      ssm_parameter_name: 'devuser',
      off_inventory: false,
    },
    {
      ssm_parameter_name: 'prod-customer-',
      off_inventory: false,
    },
    {
      ssm_parameter_name: 'prodadmin',
      off_inventory: false,
    },
    {
      ssm_parameter_name: 'prod_admin_',
      off_inventory: false,
    },
  ],
  SecretsManagerSecret: [
    {
      secret_name: 'testingadmin',
      off_inventory: false,
    },
    {
      secret_name: 'staginguser',
      off_inventory: false,
    },
    {
      secret_name: 'prod-customer-',
      off_inventory: false,
    },
    {
      secret_name: 'prod=customer=',
      off_inventory: false,
    },
    {
      secret_name: 'staging@admin@',
      off_inventory: false,
    },
    {
      secret_name: 'prodcustomer',
      off_inventory: false,
    },
    {
      secret_name: 'prod+admin+',
      off_inventory: false,
    },
  ],
});
