using System.Collections;
using System.Collections.Generic;
using System.Net;
using System;
using System.Net.Sockets;
using System.Threading;
using System.Text;
using UnityEngine;

// overall structure pilfered from here but i didn't bother extracting any of their unity files
// https://www.kodeco.com/5475-introduction-to-using-opencv-with-unity#toc-anchor-005
// this is nice because i didn't have to pay 100 dollars for the opencv plugin
// ...though i think the plugin probably does some coordinate transforms for you

// c# tuples stolen from https://thegamedev.guru/unity-c-sharp/tuples/

public class UpdatePosition : MonoBehaviour
{
    Thread receiveThread;
    UdpClient client;
    int port = 7999;
    // if we see duplicate packets, we don't want to bother doing anything
    string lastData = null;
    string lastConsumedData = null;
    

    // Start is called before the first frame update
    void Start()
    {
        InitUDP();
    }

    // Update is called once per frame
    void Update()
    {
        if (lastData != null && 
            ((lastConsumedData != null && lastConsumedData != lastData) || lastConsumedData == null)) // last cond is first time it runs
        {
            //Debug.Log("got data: " + lastData);
            lastConsumedData = lastData;
            // unpack string we got into usable data
            if (lastData != null && !lastData.Equals(""))
            {
                var unpacked = UnpackData(lastData);
                
                // do the rotation. wuss out and use a lookAt function :/
                Quaternion rot = Quaternion.LookRotation(new Vector3(-unpacked.f.x, unpacked.f.y, unpacked.f.z), 
                                                        new Vector3(-unpacked.u.x, unpacked.u.y, unpacked.u.z));
                transform.rotation = rot;

                // do the translation
                Vector3 unityPos = new Vector3(-unpacked.pos.x, unpacked.pos.z, -unpacked.pos.y);
                transform.position = unityPos;
            }
        } 
    }

    private (Vector3 pos, Vector3 f, Vector3 u) UnpackData(string data)
    {
        string[] parts = data.Split("|");
        char[] trim = { '(', ')' }; // why doesn't substring use a stop index. why is it like this

        // position
        string[] posCoords = parts[0].Substring(parts[0].IndexOf("(")).Trim(trim).Split(" ");
        Vector3 pos = new Vector3(float.Parse(posCoords[0]), float.Parse(posCoords[1]), float.Parse(posCoords[2]));

        // forward
        string[] fCoords = parts[1].Substring(parts[1].IndexOf("(")).Trim(trim).Split(" ");
        Vector3 f = new Vector3(float.Parse(fCoords[0]), float.Parse(fCoords[1]), float.Parse(fCoords[2]));

        // up
        string[] uCoords = parts[2].Substring(parts[2].IndexOf("(")).Trim(trim).Split(" ");
        Vector3 u = new Vector3(float.Parse(uCoords[0]), float.Parse(uCoords[1]), float.Parse(uCoords[2]));

        return (pos, f, u);
    }

    private Quaternion RHCQuaternionToLHCQuaternion(Quaternion quat)
    {
        // gonna be honest with you: i just sort of waved the box around to figure out how this should go
        // i may have done this wrong, because i've seen references to needing to flip w
        return new Quaternion(-quat.x, -quat.z, -quat.y, quat.w);
    }

    private void InitUDP()
    {
        Debug.Log("UDP connection get!");
        receiveThread = new Thread(new ThreadStart(ReceiveData));
        receiveThread.IsBackground = true; // run alongside other code, supposedly
        receiveThread.Start();
    }

    private void ReceiveData()
    {
        client = new UdpClient(port);
        while (true)
        {
            try
            {
                // unclear why this is 0.0.0.0 and not localhost or 127.etc
                IPEndPoint anyIP = new IPEndPoint(IPAddress.Parse("0.0.0.0"), port);

                byte[] data = client.Receive(ref anyIP);
                string text = Encoding.UTF8.GetString(data);
                if (!text.Equals("")) {
                    lastData = text;
                }
            } 
            catch (Exception e)
            {
                Debug.Log("err: " + e.ToString());
            }
        }
    }
}
