/*
 *	EDM Statistic Class
 */

package jpl.eda.xmlquery;

import java.io.*;
import java.util.*;
import jpl.eda.Configuration;
import jpl.eda.util.DOMParser;
import jpl.eda.util.*;
import org.w3c.dom.*;
import org.xml.sax.*;

/**
 * EDM Statisti class. 
 */
public class Statistic implements java.io.Serializable, Cloneable 
{
        /** Serial version unique ID. */
        static final long serialVersionUID = 8611279755682736062L;
	
        /** URL. */
	private String url;

	/** Time. */
	private long time;

	public Statistic()
        {
		url = new String("UNKNOWN");
		time = 0;
	}

	/** Constructor.
	 *
	 * @param url  The server's URL. 
	 * @param time The search time used by the server indicted by url.
         */
	public Statistic(String url, long time) 
	{
		this.url=url;
		this.time= time;
	}

         /**
         * Instantiates an Statistic instance from an Statistic structure in DOM node format.
         *
         * @param root  The DOM node.
         */
	public Statistic(Node root)
	{
		Node node;
	        String nodeName;

	        for (node = root.getFirstChild();
            		node != null; node = node.getNextSibling())
        	{
                	if (node instanceof Element)
                	{
                    		nodeName = node.getNodeName();
                    		if (nodeName.compareTo("url") == 0)
                        	   url = XML.unwrappedText(node);
                    		else
                    		if (nodeName.compareTo("time") == 0)
                        	   time = Long.parseLong(XML.unwrappedText(node));
                 	}
         	}
   	}

        /**
         *  doc The org.w3c.dom.Document object.
         */
	public synchronized Node toXML(Document doc) throws DOMException
  	{
                Element root = doc.createElement("statistic");
                XML.add(root, "url", url);
                XML.add(root, "time", ""+time);
                return root;
        }


        /**
         * Gets the URL string.
         *
         * @return The URL string.
         */
	public synchronized String getURL () {
		return url;
	}


        /**
         * Gets the search time
         *
         * @return the time
         */
	public synchronized long getTime()
	{
		return time;
	}
	
	/**
         * Sets the search time         */              
        public synchronized void setTime(long time)
        {
		 this.time= time;
        }

	public static void main(String[] args) throws Exception
	{
		Statistic sta = new Statistic("DDM", 1200);	// test constructor 2
		System.err.println("Profile Server:"+sta.getURL());
		System.err.println("Search time:"+sta.getTime());
		Statistic sta1 = new Statistic();		// test construct 1
		System.err.println("Profile Server:"+sta1.getURL());
                System.err.println("Search time:"+sta1.getTime());
		
		// create a document
		Document doc = XML.createDocument();
                Element StatisticNode = doc.createElement("Statistic");
                doc.appendChild(StatisticNode);
		XML.add(StatisticNode, "url", "DMIE");
		XML.add(StatisticNode, "time", ""+2000);


		Element root = doc.getDocumentElement();	//test constructor 3
		Statistic sta2 = new Statistic(root);	
		System.err.println("Profile Server:"+sta2.getURL());
                System.err.println("Search time:"+sta2.getTime());


		//test toXML()
		Node root1 = sta2.toXML(doc);
		Statistic sta3 = new Statistic(root1);
                System.err.println("Profile Server:"+sta3.getURL());
                System.err.println("Search time:"+sta3.getTime());
	}
}
