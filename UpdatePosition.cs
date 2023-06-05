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

// c# tuples stolen from https://thegamedev.guru/unity-c-sharp/tuples/

public class UpdatePosition : MonoBehaviour
{
    Thread receiveThread;
    UdpClient client;
    int port = 7999;
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
                var unpacked = UnpackDataActually(lastData);
                
                // do the rotation
                Quaternion rot = Quaternion.LookRotation(new Vector3(-unpacked.f.x, unpacked.f.y, unpacked.f.z), new Vector3(-unpacked.u.x, unpacked.u.y, unpacked.u.z));
                transform.rotation = rot;

                // do the translation
                Vector3 unityPos = new Vector3(-unpacked.pos.x, unpacked.pos.z, -unpacked.pos.y);
                transform.position = unityPos;
            }
            
            //Vector3 newPos = ConvertToVector(lastData);
            //transform.position = newPos;
        } 


        // presumably poll for positional data here somehow
        // Vector3 newPos = new Vector3(x, y, z);
        // transform.Translate(newPos - oldPos);
    }

    private (Vector3 pos, Vector3 f, Vector3 u) UnpackDataActually(string data)
    {
        string[] parts = data.Split("|");
        char[] trim = { '(', ')' };

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

    private (Vector3 f, Vector3 u) UnpackDataDifferent(string data)
    {
        string[] parts = data.Split("|");
        char[] trim = { '(', ')' };
        // forward
        string[] fCoords = parts[0].Substring(parts[0].IndexOf("(")).Trim(trim).Split(" ");
        Vector3 f = new Vector3(float.Parse(fCoords[0]), float.Parse(fCoords[1]), float.Parse(fCoords[2]));

        // up
        string[] uCoords = parts[1].Substring(parts[1].IndexOf("(")).Trim(trim).Split(" ");
        Vector3 u = new Vector3(float.Parse(uCoords[0]), float.Parse(uCoords[1]), float.Parse(uCoords[2]));

        return (f, u);
    }

    private (Vector3 pos, Quaternion rot) UnpackData(string data)
    {
        // first split into the 3 pieces
        string[] parts = data.Split("|");
        // dude why does substring not operate on a stopindex. why is it like this
        char[] trim = { '(', ')' };

        // position vector:
        string[] posCoords = parts[0].Substring(parts[0].IndexOf("(")).Trim(trim).Split(" ");
        float[] fPosCoords = { float.Parse(posCoords[0].Substring(2)), float.Parse(posCoords[1].Substring(2)), float.Parse(posCoords[2].Substring(2)) };
        // in theory, unity is y, z, -x
        Vector3 newPos = new Vector3(fPosCoords[1], fPosCoords[2], -fPosCoords[0]);
        
        // rotational axis:
        string[] axis = parts[1].Substring(parts[1].IndexOf("(")).Trim(trim).Split(" ");
        float[] fAxis = { float.Parse(axis[0].Substring(2)), float.Parse(axis[1].Substring(2)), float.Parse(axis[2].Substring(2)) };

        // rotational angle:
        string angle = parts[2].Substring(parts[2].IndexOf("(")).Trim(trim);
        float fAngle = float.Parse(angle);

        // make a quaternion out of it:
        //Quaternion quat = new Quaternion(fAxis[0], fAxis[1], fAxis[2], fAngle);
        Vector3 vAxis = new Vector3(fAxis[0], fAxis[1], fAxis[2]);
        Quaternion quat = Quaternion.AngleAxis(fAngle * Mathf.Rad2Deg, vAxis);
        quat = RHCQuaternionToLHCQuaternion(quat);

        return (newPos, quat);
    }

    private Quaternion RHCQuaternionToLHCQuaternion(Quaternion quat)
    {
        return new Quaternion(-quat.x, -quat.z, -quat.y, quat.w);
    }

    private Vector3 ConvertToVector(string dataString)
    {
        string[] split = dataString.Split(" ");
        // try x = camy?
        float xUnity = float.Parse(split[1].Substring(2));
        // y in unity space is camz
        float yUnity = float.Parse(split[2].Substring(2));
        // try z = -camx?
        float zUnity = float.Parse(split[0].Substring(2)) * -1;
        return new Vector3(xUnity, yUnity, zUnity);

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
                // unclear why this is 0.0.0.0 and not localhost
                IPEndPoint anyIP = new IPEndPoint(IPAddress.Parse("0.0.0.0"), port);

                byte[] data = client.Receive(ref anyIP);
                string text = Encoding.UTF8.GetString(data);
                if (!text.Equals("")) { // this needs to mark whatever our data starts with
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
